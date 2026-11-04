import { Editor } from '@tiptap/core';
import StarterKit from '@tiptap/starter-kit';
import CodeBlock from '@tiptap/extension-code-block';
import { TableKit } from '@tiptap/extension-table';

const root = document.querySelector('#tt-tiptap-app');

if (root) {
  const apiUrl = root.dataset.apiUrl;
  const editorElement = document.querySelector('#tt-tiptap-editor');
  const titleInput = document.querySelector('#tt-tiptap-title');
  const draftSelect = document.querySelector('#tt-tiptap-draft-list');
  const saveButton = document.querySelector('#tt-tiptap-save');
  const newButton = document.querySelector('#tt-tiptap-new');
  const saveStatus = document.querySelector('#tt-tiptap-save-status');
  const documentMeta = document.querySelector('#tt-tiptap-document-meta');
  const tableTools = document.querySelector('#tt-tiptap-table-tools');
  const blockStyle = document.querySelector('#tt-tiptap-block-style');
  const csrfToken = document.querySelector(
    '.tt-tiptap-csrf input[name="csrfmiddlewaretoken"]',
  )?.value || '';

  const emptyDocument = {
    format: 'tradethesis.lesson-document',
    version: 1,
    document: {
      type: 'doc',
      content: [{ type: 'paragraph' }],
    },
  };

  let editor = null;
  let activeDraftId = null;
  let activeRevision = null;
  let dirty = false;
  let suppressUpdates = false;
  let saving = false;
  let loading = false;

  const setStatus = (message, tone = 'neutral') => {
    saveStatus.textContent = message;
    saveStatus.dataset.tone = tone;
  };

  const setDirty = (value = true) => {
    dirty = value;
    saveButton.disabled = saving || loading || !editor || !dirty;
    if (dirty && !saving && !loading) {
      setStatus('Unsaved changes', 'dirty');
    }
  };

  const getEnvelope = () => ({
    format: 'tradethesis.lesson-document',
    version: 1,
    document: editor.getJSON(),
  });

  const requestJson = async (url, options = {}) => {
    const headers = new Headers(options.headers || {});
    headers.set('Accept', 'application/json');
    if (options.method && options.method !== 'GET') {
      headers.set('Content-Type', 'application/json');
      headers.set('X-CSRFToken', csrfToken);
    }
    const response = await fetch(url, {
      credentials: 'same-origin',
      cache: 'no-store',
      ...options,
      headers,
    });
    const contentType = response.headers.get('content-type') || '';
    const payload = contentType.includes('application/json')
      ? await response.json()
      : {};
    if (!response.ok) {
      const error = new Error(
        payload.detail || `Request failed with status ${response.status}.`,
      );
      error.status = response.status;
      error.payload = payload;
      throw error;
    }
    return payload;
  };

  const setEditorDocument = (envelope) => {
    if (!envelope || envelope.format !== 'tradethesis.lesson-document'
      || envelope.version !== 1 || !envelope.document) {
      throw new Error('This pilot draft uses an unsupported document format.');
    }
    suppressUpdates = true;
    try {
      const accepted = editor.commands.setContent(envelope.document, {
        emitUpdate: false,
        errorOnInvalidContent: true,
      });
      if (accepted === false) {
        throw new Error('The editor could not read this structured document.');
      }
      editor.setEditable(true);
    } finally {
      suppressUpdates = false;
    }
    updateToolbarState();
  };

  const refreshDraftList = async (selectedId = activeDraftId) => {
    const payload = await requestJson(apiUrl);
    draftSelect.replaceChildren();
    const placeholder = document.createElement('option');
    placeholder.value = '';
    placeholder.textContent = payload.drafts.length
      ? 'Open a saved pilot draft…'
      : 'No saved pilot drafts yet';
    draftSelect.append(placeholder);

    payload.drafts.forEach((draft) => {
      const option = document.createElement('option');
      option.value = draft.id;
      option.textContent = draft.title;
      draftSelect.append(option);
    });
    draftSelect.value = selectedId || '';
  };

  const loadDraft = async (draftId) => {
    if (!draftId) return;
    loading = true;
    saveButton.disabled = true;
    setStatus('Opening pilot draft…');
    try {
      const payload = await requestJson(`${apiUrl}?id=${encodeURIComponent(draftId)}`);
      setEditorDocument(payload.document);
      activeDraftId = payload.draft.id;
      activeRevision = payload.draft.revision;
      titleInput.value = payload.draft.title;
      dirty = false;
      documentMeta.textContent = `Structured document v1 · Revision ${activeRevision}`;
      setStatus('Saved draft loaded', 'saved');
      draftSelect.value = activeDraftId;
    } catch (error) {
      setStatus(error.message || 'Could not open this pilot draft.', 'error');
      draftSelect.value = activeDraftId || '';
    } finally {
      loading = false;
      saveButton.disabled = saving || !dirty;
    }
  };

  const saveDraft = async () => {
    if (!editor || saving || loading) return;
    const title = titleInput.value.trim();
    if (!title) {
      titleInput.focus();
      setStatus('Add a title before saving.', 'error');
      return;
    }
    saving = true;
    saveButton.disabled = true;
    saveButton.textContent = 'Saving…';
    setStatus('Saving sandbox draft…');
    const body = {
      title,
      document: getEnvelope(),
    };
    if (activeDraftId) {
      body.id = activeDraftId;
      body.revision = activeRevision;
    }

    try {
      const payload = await requestJson(apiUrl, {
        method: 'POST',
        body: JSON.stringify(body),
      });
      activeDraftId = payload.draft.id;
      activeRevision = payload.draft.revision;
      dirty = false;
      await refreshDraftList(activeDraftId);
      documentMeta.textContent = `Structured document v1 · Revision ${activeRevision}`;
      setStatus('Sandbox draft saved', 'saved');
    } catch (error) {
      if (error.status === 409) {
        setStatus(
          'This draft changed in another session. Reopen it before saving.',
          'error',
        );
      } else {
        setStatus(error.message || 'The draft could not be saved.', 'error');
      }
    } finally {
      saving = false;
      saveButton.textContent = 'Save sandbox draft';
      saveButton.disabled = !dirty;
    }
  };

  const startNewDraft = () => {
    if (dirty && !window.confirm('Discard the unsaved changes in this pilot draft?')) {
      return;
    }
    activeDraftId = null;
    activeRevision = null;
    titleInput.value = 'Untitled pilot lesson';
    setEditorDocument(emptyDocument);
    dirty = false;
    draftSelect.value = '';
    documentMeta.textContent = 'Structured document v1 · New sandbox draft';
    setStatus('New sandbox draft · not saved', 'neutral');
    saveButton.disabled = false;
    titleInput.focus();
    titleInput.select();
  };

  const updateToolbarState = () => {
    if (!editor) return;
    const activeStates = {
      bold: 'bold',
      italic: 'italic',
      underline: 'underline',
      strike: 'strike',
      code: 'code',
      bulletList: 'bulletList',
      orderedList: 'orderedList',
      blockquote: 'blockquote',
    };
    Object.entries(activeStates).forEach(([command, markOrNode]) => {
      const button = document.querySelector(
        `.tt-tiptap-toolbar [data-command="${command}"]`,
      );
      if (!button) return;
      const active = editor.isActive(markOrNode);
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
    });

    tableTools.hidden = !editor.isActive('table');
    if (editor.isActive('heading', { level: 1 })) blockStyle.value = '1';
    else if (editor.isActive('heading', { level: 2 })) blockStyle.value = '2';
    else if (editor.isActive('heading', { level: 3 })) blockStyle.value = '3';
    else blockStyle.value = 'paragraph';
  };

  const runToolbarCommand = (command) => {
    if (!editor) return;
    const chain = editor.chain().focus();
    let result = false;

    switch (command) {
      case 'bold': result = chain.toggleBold().run(); break;
      case 'italic': result = chain.toggleItalic().run(); break;
      case 'underline': result = chain.toggleUnderline().run(); break;
      case 'strike': result = chain.toggleStrike().run(); break;
      case 'code': result = chain.toggleCode().run(); break;
      case 'bulletList': result = chain.toggleBulletList().run(); break;
      case 'orderedList': result = chain.toggleOrderedList().run(); break;
      case 'blockquote': result = chain.toggleBlockquote().run(); break;
      case 'codeBlock': result = chain.toggleCodeBlock().run(); break;
      case 'horizontalRule': result = chain.setHorizontalRule().run(); break;
      case 'insertTable':
        result = chain.insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run();
        break;
      case 'addRowAfter': result = chain.addRowAfter().run(); break;
      case 'deleteRow': result = chain.deleteRow().run(); break;
      case 'addColumnAfter': result = chain.addColumnAfter().run(); break;
      case 'deleteColumn': result = chain.deleteColumn().run(); break;
      case 'mergeCells': result = chain.mergeCells().run(); break;
      case 'splitCell': result = chain.splitCell().run(); break;
      case 'deleteTable': result = chain.deleteTable().run(); break;
      case 'undo': result = chain.undo().run(); break;
      case 'redo': result = chain.redo().run(); break;
      case 'link': {
        const current = editor.getAttributes('link').href || '';
        const href = window.prompt('Link destination', current);
        if (href === null) return;
        if (!href.trim()) result = chain.extendMarkRange('link').unsetLink().run();
        else result = chain.extendMarkRange('link').setLink({ href: href.trim() }).run();
        break;
      }
      default:
        return;
    }
    if (!result) {
      setStatus('That action is not available for the current selection.', 'neutral');
    }
    updateToolbarState();
  };

  editor = new Editor({
    element: editorElement,
    extensions: [
      StarterKit.configure({
        heading: { levels: [1, 2, 3] },
        codeBlock: false,
        link: { openOnClick: false },
      }),
      CodeBlock.extend({
        addAttributes() {
          return {
            ...this.parent?.(),
            language: {
              default: null,
              parseHTML: (element) => element.getAttribute('data-language'),
              renderHTML: (attributes) => (
                attributes.language ? { 'data-language': attributes.language } : {}
              ),
            },
          };
        },
      }),
      TableKit.configure({
        table: {
          resizable: true,
          cellMinWidth: 80,
          HTMLAttributes: { class: 'tt-pilot-table' },
        },
      }),
    ],
    content: emptyDocument.document,
    enableContentCheck: true,
    onUpdate: () => {
      if (suppressUpdates || loading) return;
      setDirty(true);
      updateToolbarState();
    },
  });

  editor.on('selectionUpdate', updateToolbarState);
  editor.on('transaction', updateToolbarState);
  editor.on('contentError', () => {
    editor.setEditable(false);
    saveButton.disabled = true;
    setStatus(
      'This document contains content the pilot does not support. It is read-only here.',
      'error',
    );
  });

  document.querySelectorAll('.tt-tiptap-toolbar [data-command]').forEach((button) => {
    button.addEventListener('click', () => runToolbarCommand(button.dataset.command));
  });

  blockStyle.addEventListener('change', () => {
    const value = blockStyle.value;
    const chain = editor.chain().focus();
    if (value === 'paragraph') chain.setParagraph().run();
    else chain.setHeading({ level: Number(value) }).run();
    updateToolbarState();
  });

  titleInput.addEventListener('input', () => setDirty(true));
  saveButton.addEventListener('click', saveDraft);
  newButton.addEventListener('click', startNewDraft);

  draftSelect.addEventListener('change', async () => {
    const nextId = draftSelect.value;
    if (!nextId || nextId === activeDraftId) {
      draftSelect.value = activeDraftId || '';
      return;
    }
    if (dirty && !window.confirm('Discard the unsaved changes and open another pilot draft?')) {
      draftSelect.value = activeDraftId || '';
      return;
    }
    await loadDraft(nextId);
  });

  setStatus('Editor ready · sandbox only', 'saved');
  documentMeta.textContent = 'Structured document v1 · New sandbox draft';
  saveButton.disabled = false;
  refreshDraftList('').catch((error) => {
    setStatus(error.message || 'Could not load the pilot draft list.', 'error');
  });
  updateToolbarState();
}
