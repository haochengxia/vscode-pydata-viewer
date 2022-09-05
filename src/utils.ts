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

export function getResourcePath(webview: vscode.Webview, context: vscode.ExtensionContext, filePath: string): string {
    //fix for windows because there path.join will use \ as separator and when we inline this string in html/js
    //we get specials strings e.g. c:\n
    // return `vscode-resource:${path.join(context.extensionPath, filePath).replace(/\\/g, '/')}`
    return `${webview.asWebviewUri(vscode.Uri.file(path.join(context.extensionPath, filePath).replace(/\\/g, '/')))}`
}