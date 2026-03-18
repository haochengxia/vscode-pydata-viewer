export type PythonPathSource = 'manual' | 'python-extension' | 'fallback';

export type PythonPathResolutionResult = {
  path: string | undefined;
  source: PythonPathSource;
  hint: string;
};

export type PythonPathResolutionInput = {
  configuredPythonPath: string;
  workspacePath: string;
  usePythonExtensionInterpreter: boolean;
  pythonExtensionPath: string | undefined;
  fallbackPythonPath: string;
};

/**
 * Pure resolver for interpreter source priority:
 * manual > python-extension > fallback
 */
export function resolvePythonPathPriority(
  input: PythonPathResolutionInput
): PythonPathResolutionResult {
  const configured = input.configuredPythonPath ?? 'default';

  if (configured !== 'default') {
    return {
      path: configured.replace('${workspaceFolder}', input.workspacePath),
      source: 'manual',
      hint: 'Please check setting: vscode-pydata-viewer.pythonPath',
    };
  }

  if (input.usePythonExtensionInterpreter && input.pythonExtensionPath) {
    return {
      path: input.pythonExtensionPath,
      source: 'python-extension',
      hint: 'Interpreter is resolved from ms-python.python active environment.',
    };
  }

  return {
    path: input.fallbackPythonPath,
    source: 'fallback',
    hint: 'Fallback to PythonShell default interpreter.',
  };
}
