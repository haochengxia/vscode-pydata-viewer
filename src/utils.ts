import * as vscode from 'vscode';
import * as path from 'path';
import { PythonShell } from 'python-shell';

const os = require('os');

const LOCAL_OS_TYPE = os.type();

export class OSUtils {
    static type = {
        macOS: 'Darwin',
        linux: 'Linux',
        windows: 'Windows_NT',
    };

    static isMacOS(): boolean {
        return LOCAL_OS_TYPE === OSUtils.type.macOS;
    }

    static isLinux(): boolean {
        return LOCAL_OS_TYPE === OSUtils.type.linux;
    }

    static isWindows(): boolean {
        return LOCAL_OS_TYPE === OSUtils.type.windows;
    }
}

export function settings() {
    return vscode.workspace.getConfiguration("PyDataViewer");
}

export function getOption(option: string) {
    let config: vscode.WorkspaceConfiguration = vscode.workspace.getConfiguration();
    return config.get(option);
}


export function getPyScriptsPath(file: string, context: vscode.ExtensionContext, webview?: vscode.Webview): string {
    if (webview) {
        const uri = vscode.Uri.file(context.asAbsolutePath(path.join("pyscripts", file)));

        return webview.asWebviewUri(uri).toString();
    }

    return context.asAbsolutePath(path.join("pyscripts", file));
}