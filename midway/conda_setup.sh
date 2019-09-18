# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/software/Anaconda3-5.1.0-el7-x86_64/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/software/Anaconda3-5.1.0-el7-x86_64/etc/profile.d/conda.sh" ]; then
        . "/software/Anaconda3-5.1.0-el7-x86_64/etc/profile.d/conda.sh"
    else
        export PATH="/software/Anaconda3-5.1.0-el7-x86_64/bin:$PATH"
    fi
fi





