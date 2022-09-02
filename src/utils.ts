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

export async function getPythonPath(): Promise<string> {
    const extension = vscode.extensions.getExtension('ms-python.python');
    if (!extension) {
        const pythonPath = settings().get<string>('pythonPath');
        return pythonPath? pythonPath : PythonShell.defaultPythonPath;
    }
    return PythonShell.defaultPythonPath;
}

export function getResourcePath(webview: vscode.Webview, context: vscode.ExtensionContext, filePath: string): string {
    //fix for windows because there path.join will use \ as separator and when we inline this string in html/js
    //we get specials strings e.g. c:\n
    // return `vscode-resource:${path.join(context.extensionPath, filePath).replace(/\\/g, '/')}`
    return `${webview.asWebviewUri(vscode.Uri.file(path.join(context.extensionPath, filePath).replace(/\\/g, '/')))}`
}

export function toFortranAbsoluteIndex(absoluteIdx: number, shape: number[]) {
    // e.g. to C like index  45 for shape (4, 5, 6)
    // [1][2][3] for shape (4, 5, 6) => 1 * (1) + 2 * (1 * 4) + 3 * (1 * 5 * 4)

    var res = 0;
    var base = 1;

    for (var i = 0; i < shape.length; i++) {
        base *= shape[i];
    }

    for (var i = 0; i < shape.length; i++) {
        // cLikeIdx.push(absoluteIdx % shape[-i]);
        base /= shape[shape.length - 1 - i];
        res += (absoluteIdx % shape[shape.length - 1 - i]) * base;
        absoluteIdx = Math.floor(absoluteIdx / shape[shape.length - 1 - i]);
    }
    return res;
}

export function toCLikeArray(array: any, shape: number[]) {
    // walk arr
    var newArray: typeof array = [];
    for (var i = 0; i < array.length; i++) {
        newArray.push(array[toFortranAbsoluteIndex(i, shape)]);
    }
    return newArray;
}

export function wrapWithSqBr(s: string) {
    return '[' + s + ']';
}

export function multiArrayToString(array: any, shape: number[]) {
    if (shape.length > 1) {
        const pieceNum: number = shape[0];
        // const pieceSize: number = array.length / pieceNum;
        var res = new Array(pieceNum);
        for (var i = 0; i < pieceNum; i++) {
            res[i] = multiArrayToString(array[i], shape.slice(1, shape.length));
        }
        return wrapWithSqBr(res.toString());
    }
    else {
        return wrapWithSqBr(array.toString());
    }
}

export function makeTableHTML(myArray: any, style = 'fixed_headers') {
    // Get table size
    const colNum = myArray[0].length;
    const rowNum = myArray.length;
    // Add table head, the first column for row ID
    var colContent = '';
    for (var i = 0; i < colNum; i++) {
        colContent += `<th>col ${i.toString()}</th>`
    }
    var tableHead =
        `<thead>
      <tr>
      <td></td>
      ${colContent}
      </tr>
      </thead>
      `
    // Add table body
    var rowContent = '';
    for (var i = 0; i < rowNum; i++) {
        var currentRow = `<td>row ${i.toString()}</td>`; // Add row ID
        for (var j = 0; j < myArray[i].length; j++) {
            currentRow += `<td>${myArray[i][j].toString()}</td>`;
        }
        rowContent += `<tr>${currentRow}</tr>`;
    }
    var tableBody =
        `<tbody>
    ${rowContent}
    </tbody>
    `
    return `<table class=${style}>
    ${tableHead}
    ${tableBody}
    </table>`;
}

export function show2DArr(array: any) {
    // Show array in an table
    // TODO: prettify it
    const tableHTML = makeTableHTML(array);
    return tableHTML;
}

export function toMultiDimArray(array: any, shape: any) {
    if (shape.length > 1) {
        const pieceNum: number = shape[0];
        const pieceSize: number = array.length / pieceNum;
        var res = new Array(pieceNum);
        for (var i = 0; i < pieceNum; i++) {
            const begin = i * pieceSize;
            const end = array.length - (pieceNum - i - 1) * pieceSize;
            res[i] = toMultiDimArray(array.slice(begin, end), shape.slice(1, shape.length));
        }
        return res;
    }
    else {
        return array;
    }
}

export function isLargerThanOne(element: any, index: any, array: any) {
    return element > 1;
}