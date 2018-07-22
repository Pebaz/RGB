[System.Reflection.Assembly]::LoadWithPartialName('Microsoft.VisualBasic') | Out-Null
$commit_msg = [Microsoft.VisualBasic.Interaction]::InputBox("Enter a commit message", "Computer", "")

pushd ..

git add *
git commit -m $commit_msg
git config credential.helper store
git push

popd