# BoxNinja

Python3 scripts to generate a ninja file to download many files from box.

## Issue

Ever had a massive amount of small sparse files to download from box?
It's _not_ fun with the default tools.

Let's speed up the process with some python box sdk tools.

## Solution

We have 3 scripts: `boxninja_create`, `boxninja_get` and `boxninja_check`.
`boxninja_create` is the one to initially invoke in order to create a ninjafile (aka `ninja.build`) and prepare a few dependencies.

`ninja` will then execute said ninjafile and invoke `boxninja_get` to download the file into a temporary file.
Finally, `boxninja_check` will verify the downloaded data in the tempfile against the sha1 hash given by box. If it matches, it will copy the file to its finally location.

## Usage

TODO: write


## Details (blogrant)

So basically, I had to download a massive amount (124 GB) in small sparse files from box.
Box web UI failed to produce a downloadable ZIP, and getting the files by hand was out of the question.

Long story short, I had a look at the BOX SDK and created the prototypes of the released scripts in this repo.

It figures, using Ninja's fast dependency tree analysis is pretty helpful if you have to resume the download process after network timeouts.
