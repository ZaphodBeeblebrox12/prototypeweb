import { Editor } from '@tiptap/core';
import { createLessonExtensions } from './schema.js';

const TOOLBAR_ACTIONS = [
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
  { label: 'Table', title: 'Insert a 3 by 3 table', command: editor => editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run(), active: editor => editor.isActive('table') },
];

function makeButton(action, editor, toolbar) {
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
    refreshToolbar(editor, toolbar);
  });
  button.dataset.action = action.label;
  return button;
}

function refreshToolbar(editor, toolbar) {
  for (const action of TOOLBAR_ACTIONS) {
    const button = toolbar.querySelector(`[data-action="${action.label}"]`);
    if (!button) continue;
    button.setAttribute('aria-pressed', action.active(editor) ? 'true' : 'false');
    button.disabled = !editor.isEditable;
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
  const content = document.createElement('div');
  content.className = 'tt-editor-content';
  content.setAttribute('aria-label', 'Lesson body');
  const error = document.createElement('p');
  error.className = 'tt-editor-error';
  error.hidden = true;
  error.setAttribute('role', 'alert');
  shell.append(toolbar, content, error);
  element.append(shell);

  let contentError = false;
  const editor = new Editor({
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
    toolbar.append(makeButton(action, editor, toolbar));
  }
  editor.on('selectionUpdate', () => refreshToolbar(editor, toolbar));
  editor.on('transaction', () => refreshToolbar(editor, toolbar));
  refreshToolbar(editor, toolbar);

  return {
    editor,
    getDocument() {
      return {
        format: 'tradethesis.lesson',
        schema_version: 1,
        content: editor.getJSON(),
      };
    },
    setEditable(value) {
      editor.setEditable(Boolean(value) && !contentError);
      refreshToolbar(editor, toolbar);
    },
    destroy() {
      if (!editor.isDestroyed) editor.destroy();
      element.replaceChildren();
      element.classList.remove('tt-editor-root');
    },
  };
}
