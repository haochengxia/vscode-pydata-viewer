# Change Log

## 0.0.15 (2025/12/01)

- Fix: Fixed python-shell dependency packaging issue.
- Fix: Added validation for custom Python path with user-friendly error messages.
- Fix: Enhanced logging for better debugging of Python script execution.

## 0.0.14 (2025/11/27)

- Feat: Enhanced formatting for pickle files (better truncation for large collections and arrays).
- Feat: Added toggle button to switch between truncated and full output modes.
- Fix: Resolved `matplotlib` backend issues by enforcing headless mode (Agg).
- Fix: Updated dependencies (`python-shell` v5, `glob` v10) to resolve deprecation warnings.
- Fix: Restored syntax highlighting colors in the preview.
- Fix: Improved handling of custom objects in pickle files.

## 0.0.13 (2024/02/28)

- Feat: use CPU to load torch files. ([pull#23](https://github.com/haochengxia/vscode-pydata-viewer/pull/23) by [blaise-tk](https://github.com/blaise-tk))

## 0.0.12 (2023/12/03)

- Feat: support to show `plt.figure` instances (matplotlib.pyplot). (the update for [issue#18](https://github.com/haochengxia/vscode-pydata-viewer/issues/18) by [beijiguang94](https://github.com/beijiguang94))

## 0.0.11 (2023/09/28)

- Feat: support pikle file with multiple obj. ([pull#16](https://github.com/haochengxia/vscode-pydata-viewer/pull/16) by [kenshi84](https://github.com/kenshi84))

## 0.0.10 (2023/04/20)

- Feat: support custom script. (the update for [issue#3](https://github.com/haochengxia/vscode-pydata-viewer/issues/3))

## 0.0.9 (2023/04/19)

- Feat: use monospace font and display blanks for pretty view.

## 0.0.8 (2023/03/29)

- Feat: script as an external file.
- Fix: encoding problem of pickle. (by [jasongzy](https://github.com/jasongzy))

## 0.0.7 (2023/03/29)

- Feat: add an extension name of pickle file, '.pickle'.

## 0.0.6 (2023/02/26)

- Feat: add icon.

## 0.0.5 (2023/02/25)

- Feat: add config `pythonPath` to customize interpreter. (the update addresses [issue#7](https://github.com/haochengxia/vscode-pydata-viewer/issues/7))
- Feat: add an extension name of pickle file, '.pck'. (by [blannoy](https://github.com/blannoy))

## 0.0.4 (2022/09/22)

- Fix: the update addresses [issue#2](https://github.com/haochengxia/vscode-pydata-viewer/issues/2)
- Feat: prettier ndarray style with shape info. (by [jasongzy](https://github.com/jasongzy))

## 0.0.3 (2022/09/05)

- Fix: error in judging torch files.

## 0.0.2 (2022/09/05)

- Fix: error in pyscript when read numpy files.

## 0.0.1 (2022/09/05)

- Initial release.
