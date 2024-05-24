#!/usr/bin/env bash

# R
rm -f ~/.Rprofile && ln -s ~/configfiles/.Rprofile ~/.Rprofile
rm -f ~/.Renviron && ln -s ~/configfiles/.Renviron ~/.Renviron

# zsh
rm -f ~/.zshrc && ln -s ~/configfiles/.zshrc ~/.zshrc
rm -f ~/.zprofile && ln -s ~/configfiles/.zprofile ~/.zprofile
rm -f ~/.p10k.zsh && ln -s ~/configfiles/.p10k.zsh ~/.p10k.zsh
rm -f ~/.oh-my-zsh/custom/aliases.zsh && ln -s ~/configfiles/.aliases ~/.oh-my-zsh/custom/aliases.zsh



# Git
rm ~/.gitconfig && ln -s configfiles/.gitconfig  ~/.gitconfig