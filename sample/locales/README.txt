xgettext -d base -o locales/base.pot strings.py
msgmerge --update locales/es/LC_MESSAGES/base.po locales/base.pot
msgfmt -o base.mo base
