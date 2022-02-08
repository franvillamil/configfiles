#!/usr/bin/env bash

# zsh
rm ~/.zshrc && ln -s ~/configfiles/.zshrc ~/.zshrc
rm ~/.p10k.zsh && ln -s ~/configfiles/.p10k.zsh ~/.p10k.zsh

# Git
rm ~/.gitconfig && ln -s configfiles/.gitconfig  ~/.gitconfig

# Atom
rm ~/.atom/config.cson && ln -s configfiles/atom/init.coffee ~/.atom/config.cson
rm ~/.atom/init.coffee && ln -s configfiles/atom/init.coffee ~/.atom/init.coffee
rm ~/.atom/keymap.cson && ln -s configfiles/atom/keymap.cson ~/.atom/keymap.cson
rm ~/.atom/snippets.cson && ln -s configfiles/atom/snippets.cson ~/.atom/snippets.cson
rm ~/.atom/styles.less && ln -s configfiles/atom/styles.less ~/.atom/styles.less
