import assert from 'node:assert/strict';
import test from 'node:test';

import { getSchema } from '@tiptap/core';

import { createLessonExtensions } from '../src/schema.js';

test('TradeThesis schema accepts common lesson content, merged tables and references', () => {
  const schema = getSchema(createLessonExtensions());
  const document = {
    type: 'doc',
    content: [
      {
        type: 'heading',
        attrs: { level: 2 },
        content: [{ type: 'text', text: 'A structured lesson' }],
      },
      {
        type: 'paragraph',
        content: [
          { type: 'text', text: 'Bold', marks: [{ type: 'bold' }] },
          { type: 'text', text: ' and underlined', marks: [{ type: 'underline' }] },
        ],
      },
      {
        type: 'codeBlock',
        attrs: { language: 'python' },
        content: [{ type: 'text', text: "print('hello')" }],
      },
      {
        type: 'orderedList',
        attrs: { start: 3 },
        content: [
          {
            type: 'listItem',
            content: [
              { type: 'paragraph', content: [{ type: 'text', text: 'First' }] },
              {
                type: 'bulletList',
                content: [
                  {
                    type: 'listItem',
                    content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Nested' }] }],
                  },
                ],
              },
            ],
          },
        ],
      },
      {
        type: 'table',
        content: [
          {
            type: 'tableRow',
            content: [
              {
                type: 'tableHeader',
                attrs: { colspan: 2, rowspan: 1, colwidth: [120, 180], align: 'center' },
                content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Merged header' }] }],
              },
            ],
          },
        ],
      },
      { type: 'ttAssetImage', attrs: { assetId: 'managed-chart-01', alt: 'Chart' } },
      { type: 'ttFigure', attrs: { figureId: 'figure-01' } },
      { type: 'ttRegionalBlock', attrs: { blockId: 'regional-risk' } },
      { type: 'ttLessonReference', attrs: { lessonId: '12345678-1234-5678-1234-567812345678' } },
      { type: 'ttProtectedVideo', attrs: { videoId: '87654321-4321-8765-4321-876543218765' } },
      { type: 'ttCourseReference', attrs: { courseId: '12345678-1234-5678-1234-567812345678', comingSoon: true } },
      { type: 'ttLessonTab', attrs: { section: 'practice' } },
      { type: 'ttLegacyReference', attrs: { token: '[[old-widget:one]]', referenceKind: 'unknown' } },
    ],
  };

  const node = schema.nodeFromJSON(document);
  node.check();
  assert.equal(node.childCount, 13);
  const mergedCell = node.toJSON().content[3].content[0].content[0];
  assert.equal(mergedCell.attrs.colspan, 2);
  assert.deepEqual(mergedCell.attrs.colwidth, [120, 180]);
  assert.equal(mergedCell.attrs.align, 'center');
});

test('TradeThesis schema refuses unknown content node types', () => {
  const schema = getSchema(createLessonExtensions());
  assert.throws(() => schema.nodeFromJSON({
    type: 'doc',
    content: [{ type: 'unregisteredWidget' }],
  }));
});
