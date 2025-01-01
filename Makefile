.SUFFIXES: .aux .bbl .bib .blg .dvi .htm .html .css .log .out .pdf .ps .tex \
	.toc .foo .bar

LIJST = group ode field smooth_manifold riemannian_manifold lie_group

VENV_DIR = .venv
VENV_PYTHON = $(VENV_DIR)/Scripts/python

WEBDIR=../WEB
WEBTAG=../WEB/tags

$(WEBDIR):
	mkdir -p $(WEBDIR)


.PHONY: web
web: $(WEBDIR)
	@echo "======================================================="
	@echo "||                  Making Book                      ||"
	@echo "======================================================="
	python3 ./tools/web_book.py "$(CURDIR)" > $(WEBDIR)/book.tex

toutf8: $(WEBDIR)/book.tex
	@echo "======================================================="
	@echo "||             Converting to  UTF-8                  ||"
	@echo "======================================================="
	python3 ./tools/convert_utf8.py "$(WEBDIR)/book.tex" 

tag: $(WEBDIR)/book.tex
	@echo "======================================================="
	@echo "||                  Making tags                      ||"
	@echo "======================================================="
	python3 ./tools/tagger.py "$(WEBDIR)/book.tex" >> $(WEBTAG)

plastex: web toutf8 tag
	plastex --dir="../WEB/book/" --renderer=Gerby ../WEB/book.tex
	mv $(CURDIR)/book.paux ../WEB/book.paux

update: $(WEBDIR)/book/ $(WEBDIR)/tags
	cd .. && $(VENV_PYTHON) ./note/tools/update.py
