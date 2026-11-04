import { Node, mergeAttributes } from '@tiptap/core';

function referenceCard({ label, referenceAttribute, dataAttribute, marker, extraAttributes = {}, defaultReferenceValue = null }) {
  return Node.create({
    name: marker,
    group: 'block',
    atom: true,
    draggable: true,
    isolating: true,

    addAttributes() {
      return {
        [referenceAttribute]: {
          default: defaultReferenceValue,
          parseHTML: element => element.getAttribute(dataAttribute) || defaultReferenceValue,
          renderHTML: attributes => ({
            [dataAttribute]: attributes[referenceAttribute],
          }),
        },
        ...extraAttributes,
      };
    },

    parseHTML() {
      return [{ tag: `div[data-tt-node="${marker}"]` }];
    },

    renderHTML({ HTMLAttributes }) {
      return [
        'div',
        mergeAttributes(
          { 'data-tt-node': marker, class: 'tt-editor-reference' },
          HTMLAttributes,
        ),
        ['span', { class: 'tt-editor-reference__label' }, label],
      ];
    },

    addNodeView() {
      return ({ node }) => {
        const dom = document.createElement('div');
        dom.className = 'tt-editor-reference';
        dom.dataset.ttNode = marker;
        const labelElement = document.createElement('strong');
        labelElement.className = 'tt-editor-reference__label';
        const detail = document.createElement('span');
        detail.className = 'tt-editor-reference__detail';
        dom.append(labelElement, detail);

        const update = currentNode => {
          labelElement.textContent = label;
          const value = currentNode.attrs[referenceAttribute];
          detail.textContent = value ? `Reference · ${value}` : 'Reference needs attention';
          dom.dataset[referenceAttribute] = value || '';
        };
        update(node);

        return {
          dom,
          update(nextNode) {
            if (nextNode.type !== node.type) return false;
            node = nextNode;
            update(node);
            return true;
          },
        };
      };
    },
  });
}

function assetImageNode(options) {
  return Node.create({
    name: 'ttAssetImage',
    group: 'block',
    atom: true,
    draggable: true,
    isolating: true,

    addAttributes() {
      return {
        assetId: { default: null, parseHTML: element => element.getAttribute('data-asset-id') },
        alt: { default: '', parseHTML: element => element.getAttribute('data-alt') || '' },
        title: { default: '', parseHTML: element => element.getAttribute('data-title') || '' },
        caption: { default: '', parseHTML: element => element.getAttribute('data-caption') || '' },
        width: { default: null, parseHTML: element => Number(element.getAttribute('data-width')) || null },
        height: { default: null, parseHTML: element => Number(element.getAttribute('data-height')) || null },
        display: { default: 'block', parseHTML: element => element.getAttribute('data-display') || 'block' },
      };
    },

    parseHTML() {
      return [{ tag: 'figure[data-tt-node="asset-image"]' }];
    },

    renderHTML({ HTMLAttributes }) {
      return [
        'figure',
        mergeAttributes({ 'data-tt-node': 'asset-image' }, HTMLAttributes),
        ['figcaption', {}, HTMLAttributes['data-caption'] || 'Managed course image'],
      ];
    },

    addNodeView() {
      return ({ node }) => {
        const dom = document.createElement('figure');
        dom.className = 'tt-editor-asset';
        dom.dataset.ttNode = 'asset-image';
        const image = document.createElement('img');
        image.loading = 'lazy';
        image.decoding = 'async';
        const placeholder = document.createElement('div');
        placeholder.className = 'tt-editor-asset__placeholder';
        const caption = document.createElement('figcaption');
        dom.append(image, placeholder, caption);

        const update = currentNode => {
          const attrs = currentNode.attrs;
          dom.dataset.assetId = attrs.assetId || '';
          image.alt = attrs.alt || '';
          image.title = attrs.title || '';
          if (attrs.width) image.width = attrs.width;
          else image.removeAttribute('width');
          if (attrs.height) image.height = attrs.height;
          else image.removeAttribute('height');
          const url = typeof options.resolveAssetUrl === 'function'
            ? options.resolveAssetUrl(attrs.assetId)
            : null;
          // Asset URLs must be same-origin application paths. Never accept a
          // data URL, storage key, signed source URL or arbitrary remote URL here.
          const isLocalPath = typeof url === 'string' && url.startsWith('/') && !url.startsWith('//');
          if (isLocalPath) {
            image.src = url;
            image.hidden = false;
            placeholder.hidden = true;
          } else {
            image.removeAttribute('src');
            image.hidden = true;
            placeholder.hidden = false;
            placeholder.textContent = attrs.assetId
              ? `Managed image · ${attrs.assetId}`
              : 'Image reference needs an asset ID';
          }
          caption.textContent = attrs.caption || attrs.title || '';
          caption.hidden = !caption.textContent;
        };
        update(node);

        return {
          dom,
          update(nextNode) {
            if (nextNode.type !== node.type) return false;
            node = nextNode;
            update(node);
            return true;
          },
        };
      };
    },
  });
}

export function createTradeThesisReferenceNodes(options = {}) {
  return [
    assetImageNode(options),
    referenceCard({
      marker: 'ttFigure',
      label: 'Teaching figure',
      referenceAttribute: 'figureId',
      dataAttribute: 'data-figure-id',
    }),
    referenceCard({
      marker: 'ttRegionalBlock',
      label: 'Regional content block',
      referenceAttribute: 'blockId',
      dataAttribute: 'data-block-id',
    }),
    referenceCard({
      marker: 'ttLessonReference',
      label: 'Lesson reference',
      referenceAttribute: 'lessonId',
      dataAttribute: 'data-lesson-id',
    }),
    referenceCard({
      marker: 'ttProtectedVideo',
      label: 'Protected video',
      referenceAttribute: 'videoId',
      dataAttribute: 'data-video-id',
    }),
    referenceCard({
      marker: 'ttCourseReference',
      label: 'Related course card',
      referenceAttribute: 'courseId',
      dataAttribute: 'data-course-id',
      extraAttributes: {
        comingSoon: {
          default: false,
          parseHTML: element => element.getAttribute('data-coming-soon') === 'true',
          renderHTML: attributes => ({ 'data-coming-soon': String(Boolean(attributes.comingSoon)) }),
        },
      },
    }),
    referenceCard({
      marker: 'ttLessonTab',
      label: 'Lesson section marker',
      referenceAttribute: 'section',
      dataAttribute: 'data-section',
      defaultReferenceValue: 'idea',
    }),
    referenceCard({
      marker: 'ttLegacyReference',
      label: 'Unconverted legacy reference',
      referenceAttribute: 'token',
      dataAttribute: 'data-legacy-token',
      extraAttributes: {
        referenceKind: {
          default: 'unknown',
          parseHTML: element => element.getAttribute('data-reference-kind') || 'unknown',
          renderHTML: attributes => ({ 'data-reference-kind': attributes.referenceKind }),
        },
        referenceId: {
          default: null,
          parseHTML: element => element.getAttribute('data-reference-id'),
          renderHTML: attributes => ({ 'data-reference-id': attributes.referenceId }),
        },
      },
    }),
  ];
}
