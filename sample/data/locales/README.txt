xgettext -d base -o data/locales/base.pot i18n/strings.py
msgmerge --update data/locales/es/LC_MESSAGES/base.po data/locales/base.pot
msgfmt -o base.mo base
