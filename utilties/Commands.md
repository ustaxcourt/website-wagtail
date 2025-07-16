To get a list of objects in a bucket:

```
aws s3api list-objects-v2 \
--bucket <bucket_name> \
--prefix documents/ \
--query 'Contents[].[Key]' \
--output text | sed 's|^documents/||' > documents_object_list.txt
```
