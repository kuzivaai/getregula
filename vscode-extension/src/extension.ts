import * as vscode from 'vscode';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

let diagnosticCollection: vscode.DiagnosticCollection;

export function activate(context: vscode.ExtensionContext): void {
    diagnosticCollection = vscode.languages.createDiagnosticCollection('regula');
    context.subscriptions.push(diagnosticCollection);

    // Scan on save
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument((doc) => {
            const config = vscode.workspace.getConfiguration('regula');
            if (config.get<boolean>('scanOnSave', true)) {
                scanFile(doc.uri);
            }
        })
    );

    // Manual scan command
    context.subscriptions.push(
        vscode.commands.registerCommand('regula.scanFile', () => {
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                scanFile(editor.document.uri);
            }
        })
    );

    // Scan workspace command
    context.subscriptions.push(
        vscode.commands.registerCommand('regula.scanWorkspace', () => {
            const folders = vscode.workspace.workspaceFolders;
            if (folders && folders.length > 0) {
                scanWorkspace(folders[0].uri);
            }
        })
    );

    // Code action provider for suppress/accept
    context.subscriptions.push(
        vscode.languages.registerCodeActionsProvider(
            { scheme: 'file' },
            new RegulaCodeActionProvider(),
            { providedCodeActionKinds: [vscode.CodeActionKind.QuickFix] }
        )
    );

    // Status bar
    const statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    statusBar.command = 'regula.scanWorkspace';
    statusBar.text = '$(shield) Regula';
    statusBar.tooltip = 'Click to scan workspace for EU AI Act compliance';
    statusBar.show();
    context.subscriptions.push(statusBar);
}

interface Finding {
    file: string;
    line: number;
    tier: string;
    category: string;
    description: string;
    articles?: string[];
    confidence_score: number;
    suppressed: boolean;
    open_question?: boolean;
    lifecycle_phases?: string[];
    provenance?: string;
}

/**
 * Extract findings array from Regula JSON output.
 *
 * Without --explain: envelope.data is the findings array directly.
 * With --explain: envelope.data is { findings: [...], explanations: [...] }.
 * Handle both shapes defensively.
 */
function extractFindings(stdout: string): Finding[] {
    const result = JSON.parse(stdout);
    const data = result?.data;
    if (Array.isArray(data)) {
        return data;
    }
    if (data && Array.isArray(data.findings)) {
        return data.findings;
    }
    return [];
}

const TIER_ORDER: Record<string, number> = {
    prohibited: 4,
    high_risk: 3,
    credential_exposure: 3,
    limited_risk: 2,
    minimal_risk: 1,
};

function tierToSeverity(tier: string): vscode.DiagnosticSeverity {
    switch (tier) {
        case 'prohibited':
            return vscode.DiagnosticSeverity.Error;
        case 'high_risk':
        case 'credential_exposure':
            return vscode.DiagnosticSeverity.Warning;
        case 'limited_risk':
            return vscode.DiagnosticSeverity.Information;
        default:
            return vscode.DiagnosticSeverity.Hint;
    }
}

async function scanFile(uri: vscode.Uri): Promise<void> {
    const config = vscode.workspace.getConfiguration('regula');
    const executable = config.get<string>('executablePath', 'regula');
    const scope = config.get<string>('scope', 'all');

    const args = ['check', uri.fsPath, '--format', 'json'];
    if (scope === 'production') {
        args.push('--scope', 'production');
    }

    try {
        const { stdout } = await execFileAsync(executable, args, {
            timeout: 30000,
            maxBuffer: 5 * 1024 * 1024,
        });

        const findings = extractFindings(stdout);
        updateDiagnostics(uri, findings);
    } catch (err: unknown) {
        if (isEnoent(err)) {
            vscode.window.showWarningMessage(
                'Regula not found. Install with: pip install regula-ai'
            );
            return;
        }
        // Non-zero exit codes are normal (findings found), parse stdout
        const stdout = getStdout(err);
        if (stdout) {
            try {
                const findings = extractFindings(stdout);
                updateDiagnostics(uri, findings);
            } catch {
                diagnosticCollection.delete(uri);
            }
        }
    }
}

async function scanWorkspace(uri: vscode.Uri): Promise<void> {
    const config = vscode.workspace.getConfiguration('regula');
    const executable = config.get<string>('executablePath', 'regula');
    const scope = config.get<string>('scope', 'all');

    const args = ['check', uri.fsPath, '--format', 'json'];
    if (scope === 'production') {
        args.push('--scope', 'production');
    }

    let findings: Finding[];

    try {
        const { stdout } = await execFileAsync(executable, args, {
            timeout: 120000,
            maxBuffer: 10 * 1024 * 1024,
        });
        findings = extractFindings(stdout);
    } catch (err: unknown) {
        if (isEnoent(err)) {
            vscode.window.showWarningMessage(
                'Regula not found. Install with: pip install regula-ai'
            );
            return;
        }
        const stdout = getStdout(err);
        if (!stdout) return;
        try {
            findings = extractFindings(stdout);
        } catch {
            return;
        }
    }

    // Group findings by file
    const byFile = new Map<string, Finding[]>();
    for (const f of findings) {
        const filePath = f.file;
        if (!byFile.has(filePath)) {
            byFile.set(filePath, []);
        }
        byFile.get(filePath)!.push(f);
    }

    // Clear old diagnostics and set per-file
    diagnosticCollection.clear();
    for (const [filePath, fileFindings] of byFile) {
        const fullPath = vscode.Uri.joinPath(uri, filePath);
        updateDiagnostics(fullPath, fileFindings);
    }

    const totalFindings = findings.filter(f => !f.suppressed).length;
    vscode.window.showInformationMessage(
        `Regula: ${totalFindings} finding(s) across ${byFile.size} file(s)`
    );
}

function updateDiagnostics(uri: vscode.Uri, findings: Finding[]): void {
    const config = vscode.workspace.getConfiguration('regula');
    const minTier = config.get<string>('minTier', 'limited_risk');
    const minLevel = TIER_ORDER[minTier] || 2;

    const diagnostics: vscode.Diagnostic[] = [];

    for (const f of findings) {
        if (f.suppressed) continue;
        const level = TIER_ORDER[f.tier] || 1;
        if (level < minLevel) continue;

        const line = Math.max(0, (f.line || 1) - 1);
        const range = new vscode.Range(line, 0, line, 200);

        const severity = tierToSeverity(f.tier);

        const lifecycle = f.lifecycle_phases?.[0] || 'develop';
        const articles = f.articles?.join(', ') || '';
        const message = `${f.description}${articles ? ` (${articles})` : ''} [${lifecycle}]`;

        const diagnostic = new vscode.Diagnostic(range, message, severity);
        diagnostic.source = 'regula';
        diagnostic.code = f.category;
        diagnostics.push(diagnostic);
    }

    diagnosticCollection.set(uri, diagnostics);
}

class RegulaCodeActionProvider implements vscode.CodeActionProvider {
    provideCodeActions(
        document: vscode.TextDocument,
        _range: vscode.Range,
        context: vscode.CodeActionContext,
    ): vscode.CodeAction[] {
        const actions: vscode.CodeAction[] = [];

        for (const diagnostic of context.diagnostics) {
            if (diagnostic.source !== 'regula') continue;

            const line = diagnostic.range.start.line;
            const lineText = document.lineAt(line).text;
            const indent = lineText.match(/^\s*/)?.[0] || '';

            // Suppress action
            const suppress = new vscode.CodeAction(
                'Suppress: # regula-ignore',
                vscode.CodeActionKind.QuickFix
            );
            suppress.edit = new vscode.WorkspaceEdit();
            suppress.edit.insert(
                document.uri,
                new vscode.Position(line, 0),
                `${indent}# regula-ignore\n`
            );
            suppress.diagnostics = [diagnostic];
            actions.push(suppress);

            // Accept risk action
            const accept = new vscode.CodeAction(
                'Accept risk: # regula-accept owner=TODO review=TODO',
                vscode.CodeActionKind.QuickFix
            );
            accept.edit = new vscode.WorkspaceEdit();
            accept.edit.insert(
                document.uri,
                new vscode.Position(line, 0),
                `${indent}# regula-accept owner=TODO review=TODO reason="TODO"\n`
            );
            accept.diagnostics = [diagnostic];
            actions.push(accept);
        }

        return actions;
    }
}

function isEnoent(err: unknown): boolean {
    return (
        err instanceof Error &&
        'code' in err &&
        (err as NodeJS.ErrnoException).code === 'ENOENT'
    );
}

function getStdout(err: unknown): string | undefined {
    if (err && typeof err === 'object' && 'stdout' in err) {
        const stdout = (err as { stdout: string }).stdout;
        if (typeof stdout === 'string' && stdout.length > 0) {
            return stdout;
        }
    }
    return undefined;
}

export function deactivate(): void {
    diagnosticCollection?.dispose();
}
