import * as vscode from 'vscode';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function debounce<T extends (...args: any[]) => void>(fn: T, delay: number): T {
    let timer: ReturnType<typeof setTimeout>;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return ((...args: any[]) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    }) as T;
}

let diagnosticCollection: vscode.DiagnosticCollection;
let statusBar: vscode.StatusBarItem;
let findingsTreeProvider: FindingsTreeProvider;

export function activate(context: vscode.ExtensionContext): void {
    diagnosticCollection = vscode.languages.createDiagnosticCollection('regula');
    context.subscriptions.push(diagnosticCollection);

    // Status bar
    statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    statusBar.command = 'regula.scanWorkspace';
    statusBar.text = '$(shield) Regula: 0 finding(s)';
    statusBar.tooltip = 'Click to scan workspace for EU AI Act compliance';
    statusBar.show();
    context.subscriptions.push(statusBar);

    // Findings tree view
    findingsTreeProvider = new FindingsTreeProvider();
    const treeView = vscode.window.createTreeView('regulaFindings', {
        treeDataProvider: findingsTreeProvider,
        showCollapseAll: true,
    });
    context.subscriptions.push(treeView);

    // Set initial context for viewsWelcome
    vscode.commands.executeCommand('setContext', 'regula.hasFindings', false);

    // Debounced scan for onType mode (2-second debounce to prevent excessive CLI spawns)
    const debouncedScan = debounce((uri: vscode.Uri) => scanFile(uri), 2000);

    // Scan on save (respects scanTrigger setting)
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument((doc) => {
            const config = vscode.workspace.getConfiguration('regula');
            const trigger = config.get<string>('scanTrigger', 'onSave');
            if (trigger === 'onSave' && config.get<boolean>('scanOnSave', true)) {
                scanFile(doc.uri);
            }
        })
    );

    // Scan on type with debounce
    context.subscriptions.push(
        vscode.workspace.onDidChangeTextDocument((e) => {
            const config = vscode.workspace.getConfiguration('regula');
            if (config.get<string>('scanTrigger', 'onSave') === 'onType') {
                debouncedScan(e.document.uri);
            }
        })
    );

    // Manual scan command
    context.subscriptions.push(
        vscode.commands.registerCommand('regula.scanFile', () => {
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                return scanFile(editor.document.uri);
            }
            return undefined;
        })
    );

    // Scan workspace command
    context.subscriptions.push(
        vscode.commands.registerCommand('regula.scanWorkspace', () => {
            const folders = vscode.workspace.workspaceFolders;
            if (folders && folders.length > 0) {
                return scanWorkspace(folders[0].uri);
            }
            return undefined;
        })
    );

    // Code action provider for suppress/accept/fixAll
    context.subscriptions.push(
        vscode.languages.registerCodeActionsProvider(
            { scheme: 'file' },
            new RegulaCodeActionProvider(),
            {
                providedCodeActionKinds: [
                    vscode.CodeActionKind.QuickFix,
                    vscode.CodeActionKind.SourceFixAll.append('regula'),
                ],
            }
        )
    );
}

interface Finding {
    file: string;
    line: number;
    detector_class: string;
    category: string;
    description: string;
    suggested_provisions?: string[];
    detector_priority: number;
    suppressed: boolean;
    open_question?: boolean;
    lifecycle_phases?: string[];
    provenance?: string;
}

interface DecisionResult {
    result_type: 'indication' | 'insufficient_information' | 'outside_scope_candidate';
    model_version: string;
    jurisdiction: string;
    rule_resolution: string;
}

interface ScanResponse {
    findings: Finding[];
    decision: DecisionResult;
}

/**
 * Extract findings array from Regula JSON output.
 *
 * Without --explain: envelope.data is the findings array directly.
 * With --explain: envelope.data is { findings: [...], explanations: [...] }.
 * Handle both shapes defensively.
 */
function extractScanResponse(stdout: string): ScanResponse {
    const result: unknown = JSON.parse(stdout);
    if (!result || typeof result !== 'object' || Array.isArray(result)) {
        throw new Error('Regula CLI response must be an object envelope');
    }
    const envelope = result as Record<string, unknown>;
    if (typeof envelope.format_version !== 'string' || envelope.command !== 'check') {
        throw new Error('Regula CLI response has an unsupported envelope');
    }
    const data = envelope.data;
    if (data && typeof data === 'object' && !Array.isArray(data)) {
        const record = data as Record<string, unknown>;
        const decision = validateDecision(record.decision);
        if (Array.isArray(record.detector_findings)) {
            return {
                findings: validateFindings(record.detector_findings),
                decision,
            };
        }
    }
    throw new Error('Regula CLI response does not contain detector findings and a decision');
}

function validateDecision(value: unknown): DecisionResult {
    if (!value || typeof value !== 'object' || Array.isArray(value)) {
        throw new Error('Regula CLI response does not contain a decision object');
    }
    const decision = value as Record<string, unknown>;
    const validTypes = ['indication', 'insufficient_information', 'outside_scope_candidate'];
    if (
        typeof decision.result_type !== 'string' ||
        !validTypes.includes(decision.result_type) ||
        typeof decision.model_version !== 'string' ||
        typeof decision.jurisdiction !== 'string' ||
        typeof decision.rule_resolution !== 'string'
    ) {
        throw new Error('Regula CLI decision has an unsupported shape');
    }
    return decision as unknown as DecisionResult;
}

function validateFindings(values: unknown[]): Finding[] {
    for (const [index, value] of values.entries()) {
        if (!value || typeof value !== 'object' || Array.isArray(value)) {
            throw new Error(`Regula finding ${index} must be an object`);
        }
        const finding = value as Record<string, unknown>;
        if (
            typeof finding.file !== 'string' ||
            typeof finding.line !== 'number' ||
            typeof finding.detector_class !== 'string' ||
            typeof finding.category !== 'string' ||
            typeof finding.description !== 'string' ||
            typeof finding.detector_priority !== 'number' ||
            typeof finding.suppressed !== 'boolean'
        ) {
            throw new Error(`Regula finding ${index} has an unsupported shape`);
        }
    }
    return values as Finding[];
}

function showScanFailure(scope: 'file' | 'workspace'): void {
    statusBar.text = '$(error) Regula: scan failed';
    statusBar.tooltip = 'The last scan failed. Existing diagnostics may be stale.';
    void vscode.window.showErrorMessage(
        `Regula: ${scope} scan failed. Existing diagnostics were preserved and may be stale.`
    );
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
    const startTime = Date.now();
    const config = vscode.workspace.getConfiguration('regula');
    const executable = config.get<string>('executablePath', 'regula');
    const scope = config.get<string>('scope', 'all');

    const args = ['check', uri.fsPath, '--format', 'json'];
    if (scope === 'production') {
        args.push('--scope', 'production');
    }

    statusBar.text = '$(sync~spin) Regula: scanning...';

    try {
        const { stdout } = await execFileAsync(executable, args, {
            timeout: 30000,
            maxBuffer: 5 * 1024 * 1024,
        });

        const response = extractScanResponse(stdout);
        const findings = response.findings;
        updateDiagnostics(uri, findings);
        updateFindingsTree(uri, findings);
        updateStatusBarCount(response.decision);
    } catch (err: unknown) {
        if (isEnoent(err)) {
            statusBar.text = '$(shield) Regula: CLI not found';
            vscode.window.showWarningMessage(
                'Regula not found. Install from the reviewed source; see docs/installation.md'
            );
            return;
        }
        // Non-zero exit codes are normal (findings found), parse stdout
        const stdout = getStdout(err);
        if (stdout) {
            try {
                const response = extractScanResponse(stdout);
                const findings = response.findings;
                updateDiagnostics(uri, findings);
                updateFindingsTree(uri, findings);
                updateStatusBarCount(response.decision);
            } catch {
                showScanFailure('file');
            }
        } else {
            showScanFailure('file');
        }
    }

    // Time budget warning
    const elapsed = Date.now() - startTime;
    if (elapsed > 8000) {
        vscode.window.showWarningMessage(
            `Regula: Scan took ${(elapsed / 1000).toFixed(1)}s. Consider using --scope production or excluding test files.`
        );
    } else if (elapsed > 4000) {
        console.log(`Regula: Scan took ${(elapsed / 1000).toFixed(1)}s`);
    }
}

async function scanWorkspace(uri: vscode.Uri): Promise<void> {
    await vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: 'Regula: Scanning workspace...',
            cancellable: false,
        },
        async (progress) => {
            const startTime = Date.now();
            const config = vscode.workspace.getConfiguration('regula');
            const executable = config.get<string>('executablePath', 'regula');
            const scope = config.get<string>('scope', 'all');

            const args = ['check', uri.fsPath, '--format', 'json'];
            if (scope === 'production') {
                args.push('--scope', 'production');
            }

            statusBar.text = '$(sync~spin) Regula: scanning workspace...';
            progress.report({ message: 'Analysing files...' });

            let response: ScanResponse;

            try {
                const { stdout } = await execFileAsync(executable, args, {
                    timeout: 120000,
                    maxBuffer: 10 * 1024 * 1024,
                });
                response = extractScanResponse(stdout);
            } catch (err: unknown) {
                if (isEnoent(err)) {
                    statusBar.text = '$(shield) Regula: CLI not found';
                    vscode.window.showWarningMessage(
                        'Regula not found. Install from the reviewed source; see docs/installation.md'
                    );
                    return;
                }
                const stdout = getStdout(err);
                if (!stdout) {
                    showScanFailure('workspace');
                    return;
                }
                try {
                    response = extractScanResponse(stdout);
                } catch {
                    showScanFailure('workspace');
                    return;
                }
            }

            const findings = response.findings;
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
            findingsTreeProvider.clear();

            progress.report({ message: 'Updating diagnostics...' });

            for (const [filePath, fileFindings] of byFile) {
                const fullPath = vscode.Uri.joinPath(uri, filePath);
                updateDiagnostics(fullPath, fileFindings);
                updateFindingsTree(fullPath, fileFindings);
            }

            updateStatusBarCount(response.decision);

            const elapsed = Date.now() - startTime;
            const totalFindings = findings.filter(f => !f.suppressed).length;
            vscode.window.showInformationMessage(
                `Regula: ${totalFindings} finding(s) across ${byFile.size} file(s)`
            );

            // Time budget warning (Gap 3)
            if (elapsed > 8000) {
                vscode.window.showWarningMessage(
                    `Regula: Workspace scan took ${(elapsed / 1000).toFixed(1)}s. Consider using --scope production or excluding test files.`
                );
            } else if (elapsed > 4000) {
                console.log(`Regula: Workspace scan took ${(elapsed / 1000).toFixed(1)}s`);
            }
        }
    );
}

function updateDiagnostics(uri: vscode.Uri, findings: Finding[]): void {
    const config = vscode.workspace.getConfiguration('regula');
    const minTier = config.get<string>('minTier', 'limited_risk');
    const minLevel = TIER_ORDER[minTier] || 2;

    const diagnostics: vscode.Diagnostic[] = [];

    for (const f of findings) {
        if (f.suppressed) continue;
        const level = TIER_ORDER[f.detector_class] || 1;
        if (level < minLevel) continue;

        const line = Math.max(0, (f.line || 1) - 1);
        const range = new vscode.Range(line, 0, line, 200);

        const severity = tierToSeverity(f.detector_class);

        const lifecycle = f.lifecycle_phases?.[0] || 'develop';
        const articles = f.suggested_provisions?.join(', ') || '';
        const message = `${f.description}${articles ? ` (${articles})` : ''} [${lifecycle}]`;

        const diagnostic = new vscode.Diagnostic(range, message, severity);
        diagnostic.source = 'regula';
        diagnostic.code = {
            value: f.category,
            target: vscode.Uri.parse(`https://getregula.com/rules/${f.category}`),
        };
        diagnostics.push(diagnostic);
    }

    diagnosticCollection.set(uri, diagnostics);
}

function updateStatusBarCount(decision?: DecisionResult): void {
    let totalFindings = 0;
    diagnosticCollection.forEach((_uri, diagnostics) => {
        totalFindings += diagnostics.length;
    });
    statusBar.text = `$(shield) Regula: ${totalFindings} finding(s)`;
    if (decision) {
        statusBar.tooltip = (
            `Detector findings: ${totalFindings}. Legal decision: ${decision.result_type}. ` +
            `Model ${decision.model_version}; ${decision.rule_resolution} rule resolution.`
        );
    }
    vscode.commands.executeCommand('setContext', 'regula.hasFindings', totalFindings > 0);
}

function updateFindingsTree(uri: vscode.Uri, findings: Finding[]): void {
    const visible = findings.filter(f => {
        if (f.suppressed) return false;
        const config = vscode.workspace.getConfiguration('regula');
        const minTier = config.get<string>('minTier', 'limited_risk');
        const minLevel = TIER_ORDER[minTier] || 2;
        const level = TIER_ORDER[f.detector_class] || 1;
        return level >= minLevel;
    });
    findingsTreeProvider.setFindings(uri, visible);
}

// --- Tree Data Provider for Activity Bar sidebar ---

class FindingFileNode {
    constructor(
        public readonly uri: vscode.Uri,
        public readonly findings: FindingItemNode[],
    ) {}
}

class FindingItemNode {
    constructor(
        public readonly finding: Finding,
        public readonly uri: vscode.Uri,
    ) {}
}

type TreeNode = FindingFileNode | FindingItemNode;

class FindingsTreeProvider implements vscode.TreeDataProvider<TreeNode> {
    private _onDidChangeTreeData = new vscode.EventEmitter<TreeNode | undefined | void>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    private fileFindings = new Map<string, { uri: vscode.Uri; findings: Finding[] }>();

    setFindings(uri: vscode.Uri, findings: Finding[]): void {
        const key = uri.toString();
        if (findings.length === 0) {
            this.fileFindings.delete(key);
        } else {
            this.fileFindings.set(key, { uri, findings });
        }
        this._onDidChangeTreeData.fire();
    }

    clear(): void {
        this.fileFindings.clear();
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: TreeNode): vscode.TreeItem {
        if (element instanceof FindingFileNode) {
            const label = vscode.workspace.asRelativePath(element.uri);
            const item = new vscode.TreeItem(label, vscode.TreeItemCollapsibleState.Expanded);
            item.resourceUri = element.uri;
            item.iconPath = vscode.ThemeIcon.File;
            item.description = `${element.findings.length} finding(s)`;
            return item;
        }

        // FindingItemNode
        const f = element.finding;
        const tierIcon = tierToThemeIcon(f.detector_class);
        const label = `${f.category}: ${f.description}`;
        const item = new vscode.TreeItem(label, vscode.TreeItemCollapsibleState.None);
        item.iconPath = tierIcon;
        item.tooltip = `${f.detector_class}: ${f.description}${f.suggested_provisions ? ` (${f.suggested_provisions.join(', ')})` : ''}`;
        item.description = `line ${f.line || 1}`;

        // Click to navigate to the finding location
        const line = Math.max(0, (f.line || 1) - 1);
        item.command = {
            command: 'vscode.open',
            title: 'Go to finding',
            arguments: [
                element.uri,
                { selection: new vscode.Range(line, 0, line, 0) },
            ],
        };

        return item;
    }

    getChildren(element?: TreeNode): TreeNode[] {
        if (!element) {
            // Root: file nodes
            const nodes: FindingFileNode[] = [];
            for (const { uri, findings } of this.fileFindings.values()) {
                const children = findings.map(f => new FindingItemNode(f, uri));
                nodes.push(new FindingFileNode(uri, children));
            }
            return nodes;
        }

        if (element instanceof FindingFileNode) {
            return element.findings;
        }

        return [];
    }
}

function tierToThemeIcon(tier: string): vscode.ThemeIcon {
    switch (tier) {
        case 'prohibited':
            return new vscode.ThemeIcon('error', new vscode.ThemeColor('errorForeground'));
        case 'high_risk':
        case 'credential_exposure':
            return new vscode.ThemeIcon('warning', new vscode.ThemeColor('editorWarning.foreground'));
        case 'limited_risk':
            return new vscode.ThemeIcon('info', new vscode.ThemeColor('editorInfo.foreground'));
        default:
            return new vscode.ThemeIcon('lightbulb');
    }
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

        // Add "Fix All" action if multiple regula findings exist
        const regulaDiagnostics = context.diagnostics.filter(d => d.source === 'regula');
        if (regulaDiagnostics.length > 1) {
            const fixAll = new vscode.CodeAction(
                'Suppress all Regula findings in this file',
                vscode.CodeActionKind.SourceFixAll.append('regula')
            );
            fixAll.edit = new vscode.WorkspaceEdit();
            // Sort by line descending to avoid offset issues when inserting
            const sorted = [...regulaDiagnostics].sort(
                (a, b) => b.range.start.line - a.range.start.line
            );
            for (const diag of sorted) {
                const line = diag.range.start.line;
                const lineText = document.lineAt(line).text;
                const indent = lineText.match(/^\s*/)?.[0] || '';
                fixAll.edit.insert(
                    document.uri,
                    new vscode.Position(line, 0),
                    `${indent}# regula-ignore\n`
                );
            }
            fixAll.diagnostics = [...regulaDiagnostics];
            actions.push(fixAll);
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
