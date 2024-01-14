#!/usr/bin/env bash

# R
ln -s ~/configfiles/.Rprofile ~/.Rprofile
ln -s ~/configfiles/.Renviron ~/.Renviron

# zsh
rm ~/.zshrc && ln -s ~/configfiles/.zshrc ~/.zshrc
rm ~/.p10k.zsh && ln -s ~/configfiles/.p10k.zsh ~/.p10k.zsh
ln -s ~/configfiles/.aliases ~/.oh-my-zsh/custom/aliases.zsh

# Git
rm ~/.gitconfig && ln -s configfiles/.gitconfig  ~/.gitconfig