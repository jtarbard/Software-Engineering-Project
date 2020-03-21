# Git Repository Cleaning Script for Linux. Written by Vincent.

echo "$(tput setaf 2)========== Begin cleaning this Git repository ==========$(tput sgr 0)"

echo "$(tput setaf 4)>>>----->>> Ready to update all local branches <<<-----<<< $(tput sgr 0)"

git pull --all
git fetch --all
echo "$(tput setaf 4)>>>----->>> Updated all local branches <<<-----<<<$(tput sgr 0)"

echo "$(tput setaf 3)>>>----->>> Ready to clean up local branches <<<-----<<<$(tput sgr 0)"
git fetch -p > /dev/null 2>&1

# Reference: stackoverflow.com/questions/10610327/delete-all-local-git-branches
deleteMsg=$(git branch --merged master | grep -v master | grep -v stable | xargs git branch -d 2>&1)
if [ "$deleteMsg" != "fatal: branch name required" ]; then
echo "$deleteMsg"
echo "$(tput setaf 3)>>>----->>> Deleted all merged local branches <<<-----<<<$(tput sgr 0)"
else
echo "$(tput setaf 3)>>>----->>> No local branch found. Nothing needs to be deleted <<<-----<<<$(tput sgr 0)"
fi

echo "$(tput setaf 2)========== Finished automatic cleaning. Get on with your work now! ==========$(tput sgr 0)"
