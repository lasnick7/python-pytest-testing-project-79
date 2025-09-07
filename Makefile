install:
	uv sync

build:
	uv build

package-install:
	uv tool install dist/hexlet_code-0.1.0-py3-none-any.whl

test:
	uv run pytest