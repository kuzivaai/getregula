import * as vscode from 'vscode';
import { exec } from 'child_process';
import * as path from 'path';

const REGULA_DIAGNOSTIC_SOURCE = 'Regula';
const diagnosticCollection = vscode.languages.createDiagnosticCollection('regula');

export function activate(context: vscode.ExtensionContext) {
    // Run on save
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument((doc) => {
            const config = vscode.workspace.getConfiguration('regula');
            if (config.get<boolean>('runOnSave', true)) {
                checkFile(doc.uri.fsPath);
            }
        })
    );

    // Commands
    context.subscriptions.push(
        vscode.commands.registerCommand('regula.checkFile', () => {
            const editor = vscode.window.activeTextEditor;
            if (editor) checkFile(editor.document.uri.fsPath);
        }),
        vscode.commands.registerCommand('regula.checkProject', () => {
            const folder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
            if (folder) checkProject(folder);
        })
    );

    context.subscriptions.push(diagnosticCollection);
}

function checkFile(filePath: string) {
    const config = vscode.workspace.getConfiguration('regula');
    const python = config.get<string>('pythonPath', 'python3');
    const minTier = config.get<string>('minTier', 'limited_risk');
    const dir = path.dirname(filePath);

    runRegula(python, dir, filePath, minTier);
}

function runRegula(python: string, projectDir: string, filePath: string, minTier: string) {
    // Try `regula` command first, fall back to python -m regula
    const cmd = `regula check "${filePath}" --format json --min-tier ${minTier} 2>/dev/null`;

    exec(cmd, { cwd: projectDir }, (error, stdout) => {
        if (error && !stdout) {
            // Try python fallback
            const fallback = `${python} -m regula check "${filePath}" --format json --min-tier ${minTier}`;
            exec(fallback, { cwd: projectDir }, (_err, fallbackOut) => {
                parseAndShow(filePath, fallbackOut);
            });
            return;
        }
        parseAndShow(filePath, stdout);
    });
}

function checkProject(projectDir: string) {
    const config = vscode.workspace.getConfiguration('regula');
    const python = config.get<string>('pythonPath', 'python3');
    const minTier = config.get<string>('minTier', 'limited_risk');
    const cmd = `regula check "${projectDir}" --format json --min-tier ${minTier}`;

    exec(cmd, { cwd: projectDir }, (_error, stdout) => {
        try {
            const envelope = JSON.parse(stdout);
            const findings: any[] = envelope?.data?.findings || envelope?.findings || [];
            const byFile: Map<string, vscode.Diagnostic[]> = new Map();

            for (const finding of findings) {
                const file = finding.file || '';
                if (!file) continue;
                const diag = findingToDiagnostic(finding);
                if (!byFile.has(file)) byFile.set(file, []);
                byFile.get(file)!.push(diag);
            }

            diagnosticCollection.clear();
            for (const [file, diags] of byFile.entries()) {
                diagnosticCollection.set(vscode.Uri.file(file), diags);
            }
        } catch { /* non-JSON output — ignore */ }
    });
}

function parseAndShow(filePath: string, stdout: string) {
    try {
        const envelope = JSON.parse(stdout);
        const findings: any[] = envelope?.data?.findings || envelope?.findings || [];
        const diagnostics = findings
            .filter(f => f.file === filePath || f.file?.endsWith(path.basename(filePath)))
            .map(findingToDiagnostic);
        diagnosticCollection.set(vscode.Uri.file(filePath), diagnostics);
    } catch { /* non-JSON output — ignore */ }
}

function findingToDiagnostic(finding: any): vscode.Diagnostic {
    const line = Math.max(0, (finding.line || 1) - 1);
    const range = new vscode.Range(line, 0, line, 999);
    const tier = (finding.tier || '').toLowerCase();
    const severity =
        tier === 'prohibited' || tier === 'block' ? vscode.DiagnosticSeverity.Error :
        tier === 'high_risk' || tier === 'warn'   ? vscode.DiagnosticSeverity.Warning :
                                                    vscode.DiagnosticSeverity.Information;
    const diag = new vscode.Diagnostic(range, finding.description || 'Regula finding', severity);
    diag.source = REGULA_DIAGNOSTIC_SOURCE;
    diag.code = finding.article || finding.tier || '';
    return diag;
}

export function deactivate() {
    diagnosticCollection.dispose();
}
