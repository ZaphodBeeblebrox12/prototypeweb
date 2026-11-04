import { Editor } from '@tiptap/core';
import { createLessonExtensions } from './schema.js';

const TOOLBAR_ACTIONS = [
  { label: 'Undo', title: 'Undo (Ctrl+Z)', command: editor => editor.chain().focus().undo().run(), can: editor => editor.can().undo() },
  { label: 'Redo', title: 'Redo (Ctrl+Shift+Z)', command: editor => editor.chain().focus().redo().run(), can: editor => editor.can().redo() },
  { label: 'Bold', title: 'Bold (Ctrl+B)', command: editor => editor.chain().focus().toggleBold().run(), active: editor => editor.isActive('bold') },
  { label: 'Italic', title: 'Italic (Ctrl+I)', command: editor => editor.chain().focus().toggleItalic().run(), active: editor => editor.isActive('italic') },
  { label: 'Underline', title: 'Underline (Ctrl+U)', command: editor => editor.chain().focus().toggleUnderline().run(), active: editor => editor.isActive('underline') },
  { label: 'Strike', title: 'Strikethrough', command: editor => editor.chain().focus().toggleStrike().run(), active: editor => editor.isActive('strike') },
  { label: 'H2', title: 'Heading 2', command: editor => editor.chain().focus().toggleHeading({ level: 2 }).run(), active: editor => editor.isActive('heading', { level: 2 }) },
  { label: 'H3', title: 'Heading 3', command: editor => editor.chain().focus().toggleHeading({ level: 3 }).run(), active: editor => editor.isActive('heading', { level: 3 }) },
  { label: '• List', title: 'Bulleted list', command: editor => editor.chain().focus().toggleBulletList().run(), active: editor => editor.isActive('bulletList') },
  { label: '1. List', title: 'Numbered list', command: editor => editor.chain().focus().toggleOrderedList().run(), active: editor => editor.isActive('orderedList') },
  { label: 'Quote', title: 'Blockquote', command: editor => editor.chain().focus().toggleBlockquote().run(), active: editor => editor.isActive('blockquote') },
  { label: 'Code', title: 'Code block', command: editor => editor.chain().focus().toggleCodeBlock().run(), active: editor => editor.isActive('codeBlock') },
  { label: 'Left', title: 'Align text left', command: editor => editor.chain().focus().setTextAlign('left').run(), active: editor => editor.isActive({ textAlign: 'left' }) },
  { label: 'Centre', title: 'Centre text', command: editor => editor.chain().focus().setTextAlign('center').run(), active: editor => editor.isActive({ textAlign: 'center' }) },
  { label: 'Right', title: 'Align text right', command: editor => editor.chain().focus().setTextAlign('right').run(), active: editor => editor.isActive({ textAlign: 'right' }) },
  { label: 'Table', title: 'Insert a 3 by 3 table', command: editor => editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run(), active: editor => editor.isActive('table') },
];

const TABLE_ACTIONS = [
  { label: 'Row + above', title: 'Insert row above', command: editor => editor.chain().focus().addRowBefore().run(), can: editor => editor.can().addRowBefore() },
  { label: 'Row + below', title: 'Insert row below', command: editor => editor.chain().focus().addRowAfter().run(), can: editor => editor.can().addRowAfter() },
  { label: 'Delete row', title: 'Delete selected row', command: editor => editor.chain().focus().deleteRow().run(), can: editor => editor.can().deleteRow() },
  { label: 'Column + left', title: 'Insert column before', command: editor => editor.chain().focus().addColumnBefore().run(), can: editor => editor.can().addColumnBefore() },
  { label: 'Column + right', title: 'Insert column after', command: editor => editor.chain().focus().addColumnAfter().run(), can: editor => editor.can().addColumnAfter() },
  { label: 'Delete column', title: 'Delete selected column', command: editor => editor.chain().focus().deleteColumn().run(), can: editor => editor.can().deleteColumn() },
  { label: 'Merge', title: 'Merge selected cells', command: editor => editor.chain().focus().mergeCells().run(), can: editor => editor.can().mergeCells() },
  { label: 'Split', title: 'Split selected cell', command: editor => editor.chain().focus().splitCell().run(), can: editor => editor.can().splitCell() },
  { label: 'Header row', title: 'Toggle header row', command: editor => editor.chain().focus().toggleHeaderRow().run(), can: editor => editor.can().toggleHeaderRow() },
  { label: 'Delete table', title: 'Delete this table', command: editor => editor.chain().focus().deleteTable().run(), can: editor => editor.can().deleteTable() },
];

const CELL_ALIGNMENTS = [
  { label: 'Cell left', title: 'Align cell left', value: 'left' },
  { label: 'Cell centre', title: 'Align cell centre', value: 'center' },
  { label: 'Cell right', title: 'Align cell right', value: 'right' },
];

function makeButton(action, editor, toolbar, refresh) {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'tt-editor-toolbar__button';
  button.textContent = action.label;
  button.title = action.title;
  button.setAttribute('aria-label', action.title);
  button.setAttribute('aria-pressed', 'false');
  button.addEventListener('mousedown', event => event.preventDefault());
  button.addEventListener('click', () => {
    if (!editor.isDestroyed && editor.isEditable) action.command(editor);
    refresh();
  });
  button.dataset.action = action.label;
  return button;
}

function refreshButtons(editor, toolbar, actions) {
  for (const action of actions) {
    const button = toolbar.querySelector(`[data-action="${action.label}"]`);
    if (!button) continue;
    button.setAttribute('aria-pressed', action.active?.(editor) ? 'true' : 'false');
    button.disabled = !editor.isEditable || (action.can ? !action.can(editor) : false);
  }
}

function validateEnvelope(documentValue) {
  if (
    !documentValue ||
    documentValue.format !== 'tradethesis.lesson' ||
    documentValue.schema_version !== 1 ||
    !documentValue.content ||
    documentValue.content.type !== 'doc'
  ) {
    throw new TypeError('The editor requires a version 1 TradeThesis lesson document.');
  }
}

function isSafeReferenceId(value) {
  return typeof value === 'string' && /^[A-Za-z0-9_-]{1,120}$/.test(value);
}

/**
 * Mount the isolated Tiptap editor.
 *
 * This module does not save to Django. The host application owns CSRF, permissions,
 * draft IDs, persistence, optimistic concurrency and review/publish transitions.
 */
export function mountTradeThesisEditor(element, options = {}) {
  if (!(element instanceof HTMLElement)) {
    throw new TypeError('A DOM element is required to mount the lesson editor.');
  }
  validateEnvelope(options.document);

  element.replaceChildren();
  element.classList.add('tt-editor-root');

  const shell = document.createElement('section');
  shell.className = 'tt-editor-shell';
  const toolbar = document.createElement('div');
  toolbar.className = 'tt-editor-toolbar';
  toolbar.setAttribute('role', 'toolbar');
  toolbar.setAttribute('aria-label', 'Lesson formatting');
  const tableToolbar = document.createElement('div');
  tableToolbar.className = 'tt-editor-table-toolbar';
  tableToolbar.setAttribute('role', 'toolbar');
  tableToolbar.setAttribute('aria-label', 'Table editing');
  tableToolbar.hidden = true;
  const content = document.createElement('div');
  content.className = 'tt-editor-content';
  content.setAttribute('aria-label', 'Lesson body');
  const error = document.createElement('p');
  error.className = 'tt-editor-error';
  error.hidden = true;
  error.setAttribute('role', 'alert');
  shell.append(toolbar, tableToolbar, content, error);
  element.append(shell);

  let contentError = false;
  let editor;
  const refresh = () => {
    if (!editor || editor.isDestroyed) return;
    refreshButtons(editor, toolbar, TOOLBAR_ACTIONS);
    refreshButtons(editor, tableToolbar, TABLE_ACTIONS);
    const inTable = editor.isActive('table');
    tableToolbar.hidden = !inTable;
    for (const alignment of CELL_ALIGNMENTS) {
      const button = tableToolbar.querySelector(`[data-cell-align="${alignment.value}"]`);
      if (!button) continue;
      const attrs = editor.getAttributes('tableCell');
      const headerAttrs = editor.getAttributes('tableHeader');
      button.setAttribute(
        'aria-pressed',
        (attrs.align || headerAttrs.align) === alignment.value ? 'true' : 'false',
      );
      button.disabled = !editor.isEditable || !editor.can().setCellAttribute('align', alignment.value);
    }
  };

  editor = new Editor({
    element: content,
    extensions: createLessonExtensions({
      resolveAssetUrl: options.resolveAssetUrl,
    }),
    content: options.document.content,
    editable: options.editable !== false,
    enableContentCheck: true,
    onContentError({ error: schemaError }) {
      contentError = true;
      error.textContent = 'This lesson contains content the current editor schema cannot safely edit. It has been opened read-only to protect the original.';
      error.hidden = false;
      options.onError?.(schemaError);
    },
    onUpdate({ editor: currentEditor }) {
      if (contentError) return;
      options.onChange?.({
        format: 'tradethesis.lesson',
        schema_version: 1,
        content: currentEditor.getJSON(),
      });
    },
  });

  for (const action of TOOLBAR_ACTIONS) {
    toolbar.append(makeButton(action, editor, toolbar, refresh));
  }
  for (const action of TABLE_ACTIONS) {
    tableToolbar.append(makeButton(action, editor, tableToolbar, refresh));
  }
  for (const alignment of CELL_ALIGNMENTS) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'tt-editor-toolbar__button';
    button.textContent = alignment.label;
    button.title = alignment.title;
    button.setAttribute('aria-label', alignment.title);
    button.setAttribute('aria-pressed', 'false');
    button.dataset.cellAlign = alignment.value;
    button.addEventListener('mousedown', event => event.preventDefault());
    button.addEventListener('click', () => {
      if (!editor.isDestroyed && editor.isEditable) {
        editor.chain().focus().setCellAttribute('align', alignment.value).run();
      }
      refresh();
    });
    tableToolbar.append(button);
  }

  editor.on('selectionUpdate', refresh);
  editor.on('transaction', refresh);
  refresh();

  return {
    editor,
    getDocument() {
      return {
        format: 'tradethesis.lesson',
        schema_version: 1,
        content: editor.getJSON(),
      };
    },
    setDocument(documentValue) {
      validateEnvelope(documentValue);
      if (contentError) throw new Error('Cannot replace an unsupported document in a read-only editor.');
      editor.commands.setContent(documentValue.content);
    },
    setEditable(value) {
      editor.setEditable(Boolean(value) && !contentError);
      refresh();
    },
    insertReference(type, attrs) {
      const referenceTypes = new Set([
        'ttAssetImage',
        'ttFigure',
        'ttRegionalBlock',
        'ttLessonReference',
        'ttProtectedVideo',
        'ttLegacyReference',
      ]);
      if (!referenceTypes.has(type) || !editor.schema.nodes[type]) {
        throw new TypeError('Unsupported TradeThesis reference node.');
      }
      if (!attrs || typeof attrs !== 'object' || Array.isArray(attrs)) {
        throw new TypeError('Reference attributes must be an object.');
      }
      // The server will validate reference ownership and permissions on save.
      // Never pass URLs or storage keys as reference identifiers.
      const referenceId = attrs.assetId || attrs.figureId || attrs.blockId ||
        attrs.lessonId || attrs.videoId || attrs.token;
      if (type !== 'ttLegacyReference' && !isSafeReferenceId(String(referenceId || ''))) {
        throw new TypeError('A stable TradeThesis reference ID is required.');
      }
      return editor.chain().focus().insertContent({ type, attrs }).run();
    },
    destroy() {
      if (!editor.isDestroyed) editor.destroy();
      element.replaceChildren();
      element.classList.remove('tt-editor-root');
    },
  };
}
