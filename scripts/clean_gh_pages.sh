git reset --hard HEAD

git checkout gh-pages
git pull origin gh-pages

ls -la
rm -rf *
rm -rf .github
ls -la

git add .
git commit -m "[clean_gh-pages] $(date)"
git push origin gh-pages

git checkout main
open -a safari "https://github.com/nuuuwan/cbsl/tree/gh-pages"
