# LSP-slangd

Shader Slang support for Sublime's LSP plugin provided through slangd.

## Installation

- Install [LSP](https://packagecontrol.io/packages/LSP) and `LSP-slangd` from Package Control
- This package manages it's slangd executable, you can overwrite that in the settings.

## Configuration

Here are some ways to configure the package and the language server.

- From `Preferences > Package Settings > LSP > Servers > LSP-slangd`
- From the command palette: `Preferences: LSP-slangd Settings`
- Project-specific configuration.
  From the command palette run `Project: Edit Project` and add your settings in:

  ```js
  {
     "settings": {
        "LSP": {
           "slangd": {
              "settings": {
                // Put your settings here eg.
              }
           }
        }
     }
  }
  ```
