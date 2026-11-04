import StarterKit from '@tiptap/starter-kit';
import { TableKit } from '@tiptap/extension-table';
import Highlight from '@tiptap/extension-highlight';
import Placeholder from '@tiptap/extension-placeholder';
import TextAlign from '@tiptap/extension-text-align';
import { Extension } from '@tiptap/core';

import { createTradeThesisReferenceNodes } from './reference-nodes.js';

const TableCellPresentation = Extension.create({
  name: 'ttTableCellPresentation',

  addGlobalAttributes() {
    return [
      {
        types: ['table'],
        attributes: {
          caption: {
            default: '',
            parseHTML: element => element.getAttribute('data-tt-caption') || '',
            renderHTML: attributes => attributes.caption
              ? { 'data-tt-caption': attributes.caption }
              : {},
          },
          columnWidths: {
            default: null,
            parseHTML: element => {
              try {
                const value = JSON.parse(element.getAttribute('data-tt-column-widths') || 'null');
                return Array.isArray(value) ? value : null;
              } catch {
                return null;
              }
            },
            renderHTML: attributes => Array.isArray(attributes.columnWidths)
              ? { 'data-tt-column-widths': JSON.stringify(attributes.columnWidths) }
              : {},
          },
          layout: {
            default: 'auto',
            parseHTML: element => element.getAttribute('data-tt-layout') || 'auto',
            renderHTML: attributes => attributes.layout && attributes.layout !== 'auto'
              ? { 'data-tt-layout': attributes.layout }
              : {},
          },
        },
      },
      {
        types: ['tableCell', 'tableHeader'],
        attributes: {
          align: {
            default: null,
            parseHTML: element => element.getAttribute('align') || element.style.textAlign || null,
            renderHTML: attributes => attributes.align
              ? { style: `text-align: ${attributes.align}` }
              : {},
          },
          verticalAlign: {
            default: null,
            parseHTML: element => element.style.verticalAlign || null,
            renderHTML: attributes => attributes.verticalAlign
              ? { style: `vertical-align: ${attributes.verticalAlign}` }
              : {},
          },
          backgroundColor: {
            default: null,
            parseHTML: element => element.style.backgroundColor || null,
            renderHTML: attributes => attributes.backgroundColor
              ? { style: `background-color: ${attributes.backgroundColor}` }
              : {},
          },
        },
      },
    ];
  },
});

export function createLessonExtensions(options = {}) {
  return [
    StarterKit.configure({
      heading: { levels: [1, 2, 3, 4, 5, 6] },
      link: {
        openOnClick: false,
        autolink: true,
        linkOnPaste: true,
      },
    }),
    TableKit.configure({
      table: {
        resizable: true,
        lastColumnResizable: true,
        allowTableNodeSelection: true,
        cellMinWidth: 60,
      },
    }),
    TableCellPresentation,
    TextAlign.configure({
      types: ['heading', 'paragraph'],
      alignments: ['left', 'center', 'right'],
      defaultAlignment: 'left',
    }),
    Highlight.configure({ multicolor: false }),
    Placeholder.configure({
      placeholder: 'Start writing your lesson…',
      includeChildren: true,
    }),
    ...createTradeThesisReferenceNodes(options),
  ];
}
