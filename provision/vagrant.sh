# Provisioning of Vagrant user (non-root)
cd ~

# Install Python with PyEnv
if [ ! -d ~/.pyenv ]; then
    curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
    ~/.pyenv/bin/pyenv install 3.4.1
else
    echo "Skipping PyEnv installation, already installed."
fi

# Setup nicer ZSH
if [ ! -f ~/.zshrc ]; then
    zsh -c '
    git clone --recursive https://github.com/sorin-ionescu/prezto.git "${ZDOTDIR:-$HOME}/.zprezto"
    setopt EXTENDED_GLOB
    for rcfile in "${ZDOTDIR:-$HOME}"/.zprezto/runcoms/^README.md(.N); do
      ln -s "$rcfile" "${ZDOTDIR:-$HOME}/.${rcfile:t}"
    done
    '
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshenv
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshenv
    echo 'eval "$(pyenv init -)"' >> ~/.zshenv
else
    echo "Skipping Prezto installation, ZSH already set-up."
fi

# Improve VIM (Pathogen & Sensible)
if [ ! -d ~/.vim/autoload ]; then
    mkdir -p ~/.vim/autoload ~/.vim/bundle && \
    curl -LSso ~/.vim/autoload/pathogen.vim https://tpo.pe/pathogen.vim
    echo "execute pathogen#infect()" > ~/.vimrc

    cd ~/.vim/bundle && \
    git clone git://github.com/tpope/vim-sensible.git; \
    git clone git://github.com/kien/ctrlp.vim.git; \
    git clone git://github.com/ervandew/supertab.git; \
    git clone git://github.com/digitaltoad/vim-jade.git

    echo "set tabstop=2" >> ~/.vimrc
    echo "set shiftwidth=2" >> ~/.vimrc
    echo "set expandtab" >> ~/.vimrc
    echo "set noswapfile" >> ~/.vimrc
    echo "let g:ctrlp_map = '<c-p>'" >> ~/.vimrc
    echo "let g:ctrlp_cmd = 'CtrlP'" >> ~/.vimrc
    echo "map <C-j> <C-W>j" >> ~/.vimrc
    echo "map <C-k> <C-W>k" >> ~/.vimrc
    echo "map <C-h> <C-W>h" >> ~/.vimrc
    echo "map <C-l> <C-W>l" >> ~/.vimrc
    echo "set colorcolumn=80" >> ~/.vimrc
else
    echo "Skipping VIM improvements, already set-up."
fi

# Improve TMUX settings
if [ ! -f ~/.tmux.conf ]; then
    cd ~/ && wget https://gist.githubusercontent.com/bartolsthoorn/b7c7e481a1e5bda6952a/raw/719b0cfa23cbdadd5c5ddc9c228f1e6e33203c45/.tmux.conf
else
    echo "Skipping TMUX improvements, already configured."
fi

# 48 - 10.1
# TODO: Use requirements.txt to install requirements of Python with pip
