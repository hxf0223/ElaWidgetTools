#include "ElaKeyBinderPrivate.h"

#include <QTimer>

#include "ElaKeyBinder.h"
#include "ElaTheme.h"

ElaKeyBinderPrivate::ElaKeyBinderPrivate(QObject* parent)
    : QObject(parent) {}

ElaKeyBinderPrivate::~ElaKeyBinderPrivate() {}

void ElaKeyBinderPrivate::onThemeChanged(ElaThemeType::ThemeMode themeMode) {
  Q_Q(ElaKeyBinder);
  _themeMode = themeMode;
  QPalette palette = q->palette();
  palette.setColor(QPalette::WindowText, ElaThemeColor(_themeMode, BasicText));
  q->setPalette(palette);
}
