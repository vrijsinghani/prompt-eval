count=1
for file in *.jpg; do
    backgroundremover -wn 30 -i "$file" -o "clear$count.png"
#    convert "file$count.png" -resize 200x200 "file$count.png"
    ((count++))
done
