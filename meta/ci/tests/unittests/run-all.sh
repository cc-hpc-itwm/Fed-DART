#! /bin/sh
for n in `find . -name "*.py"`
do
  python $n
  ret=$?
  if [ $ret -ne 0 ]; then
     exit $ret
  fi
done
