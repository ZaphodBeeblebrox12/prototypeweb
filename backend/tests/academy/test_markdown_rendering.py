from apps.academy.templatetags.academy_markdown import render_markdown


def test_renders_markdown_tables_lists_and_headings():
    rendered = render_markdown(
        "# Read the chart\n\n- First\n- Second\n\n| Bid | Ask |\n| --- | --- |\n| 10 | 11 |"
    )

    assert "<h1>Read the chart</h1>" in rendered
    assert "<ul>" in rendered
    assert "<table>" in rendered
    assert "<td>10</td>" in rendered


def test_strips_script_tags_event_handlers_and_javascript_links():
    rendered = render_markdown(
        "<script>alert('x')</script>\n\n"
        "<img src=\"x\" onerror=\"alert(1)\">\n\n"
        "[bad link](javascript:alert(1))"
    )

    assert "<script" not in rendered.lower()
    assert "onerror" not in rendered.lower()
    assert "javascript:" not in rendered.lower()
