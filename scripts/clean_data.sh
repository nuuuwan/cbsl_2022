git reset --hard HEAD

git checkout data

rm -rf *
rm -rf .github

git add .
git commit -m "[clean_data] cleaned"
git push origin data
