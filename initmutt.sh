echo -n PASSWORD: 
read pass
echo -n E-MAIL: 
read email

mkdir ~/.mutt
mkdir ~/.mutt/cache
mkdir ~/.mutt/cache/headers
mkdir ~/.mutt/cache/bodies

echo set imap_pass=\"$pass\" > ~/.mutt/passwords
echo set smtp_pass=\"$pass\" >> ~/.mutt/passwords

gpg --gen-key

gpg -r $email -e ~/.mutt/passwords
shred ~/.mutt/passwords
rm ~/.mutt/passwords

