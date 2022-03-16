git reset --hard HEAD

git checkout data
git pull origin data

ls -la
rm -rf *
rm -rf .github
ls -la

git add .
git commit -m "[clean_data] $(date)"
git push origin data

git checkout master
