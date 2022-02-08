# Your init script
#
# Atom will evaluate this file each time a new window is opened. It is run
# after packages are loaded/activated and after the previous editor state
# has been restored.
#
# An example hack to make opened Markdown files always be soft wrapped:
#
# path = require 'path'
#
# atom.workspaceView.eachEditorView (editorView) ->
#   editor = editorView.getEditor()
#   if path.extname(editor.getPath()) is '.md'
#     editor.setSoftWrap(true)

atom.commands.add 'atom-text-editor', 'latex:toggle-bold', ->
  return unless editor = atom.workspace.getActiveTextEditor()
  selection = editor.getLastSelection()
  selection.insertText("\\textbf{#{selection.getText()}}")
  if not editor.getSelectedText()
      editor.moveLeft()

atom.commands.add 'atom-text-editor', 'latex:toggle-italic', ->
  return unless editor = atom.workspace.getActiveTextEditor()
  selection = editor.getLastSelection()
  selection.insertText("\\textit{#{selection.getText()}}")
  if not editor.getSelectedText()
      editor.moveLeft()

atom.commands.add 'atom-text-editor', 'latex:toggle-color-red', ->
  return unless editor = atom.workspace.getActiveTextEditor()
  selection = editor.getLastSelection()
  selection.insertText("{\\color{red}{#{selection.getText()}}}")
  if not editor.getSelectedText()
      editor.moveLeft()
      editor.moveLeft()

atom.commands.add 'atom-text-editor', 'latex:toggle-color-gray', ->
  return unless editor = atom.workspace.getActiveTextEditor()
  selection = editor.getLastSelection()
  selection.insertText("{\\color{gray}{#{selection.getText()}}}")
  if not editor.getSelectedText()
      editor.moveLeft()
      editor.moveLeft()

atom.commands.add 'atom-text-editor', 'latex:toggle-typewriter', ->
  return unless editor = atom.workspace.getActiveTextEditor()
  selection = editor.getLastSelection()
  selection.insertText("\\texttt{#{selection.getText()}}")
  if not editor.getSelectedText()
      editor.moveLeft()

atom.commands.add 'atom-text-editor', 'latex:toggle-verbatim', ->
  return unless editor = atom.workspace.getActiveTextEditor()
  selection = editor.getLastSelection()
  selection.insertText("\\begin{verbatim}
    #{selection.getText()}
    \\end{verbatim}")
  if not editor.getSelectedText()
      editor.moveLeft()

atom.commands.add 'atom-text-editor', 'custom:r-assigner': ->
  atom.workspace.getActiveTextEditor()?.insertText(' <- ')

atom.config.set('welcome.showOnStartup', 'false')
atom.config.set('core.automaticallyUpdate', 'false')
atom.config.set('core.telemetryConsent', 'no')

atom.config.set('welcome.showOnStartup', 'false')
atom.config.set('core.automaticallyUpdate', 'false')
atom.config.set('core.telemetryConsent', 'no')

atom.config.set('welcome.showOnStartup', 'false')
atom.config.set('core.automaticallyUpdate', 'false')
atom.config.set('core.telemetryConsent', 'no')
atom.config.set('welcome.showOnStartup', 'false')
atom.config.set('core.automaticallyUpdate', 'false')
atom.config.set('core.telemetryConsent', 'no')

atom.config.set('welcome.showOnStartup', 'false')
atom.config.set('core.automaticallyUpdate', 'false')
atom.config.set('core.telemetryConsent', 'no')
