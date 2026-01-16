Do something to make the deployment easier:
A single command which does:
- bump version (v0.0.0-pre11 -> v0.0.0-pre12)
- lint & format python & typescript
- build frontend (to test it builds)
- pushes to origin mane (including the tag)
Additionally:
- have a makefile with commands for the individual steps.
- The "Warning: You have uncommitted changes" should follow gitignore
- Sync the version numbers with the tags
- it should only increment the version after it succeeded with the tests.
- Add the GH release url and the hacs install url to `View the release at:` in the script.
- Add a `make commit` script, which:
  - first commits changes to `ai/query.md` with the message `ai: updated query`
  - secondly commits changes to `ai/errors.md` with `ai: updated errors`
  - third commit all other changes with `ai: running... ($step-$substep)` (where $substep will be reset to 1 in the script, and $step incremented compared to the last commit matching that.
- So the order will be:
  - first check for all errors except formating nitpicks
  - run commit.sh
  - run the python formatter
  - commit those changes with `lint: ruff`
  - run the ts formatter
  - commit these changes with `lint: ts`
  - build it to confirm it working
  - only now that every test was successful:
    - increase the versions
    - add the version-changed file(s) to git
    - commit a message with "version: bumped `x` -> `y`"  (a proper unicode arrow)
    - tag the commit.
    - and finally push the commit and the tag to origin mane.
- Do not use `git add --all`. I prefer only updated over all.
- Also if there's anything staged to git, remove that, and restore it afterwards (before/for the commit rest step)
- release depends on successful lint, build.

Regarding formatting:
- I don't want prettier to ever move multiline stuff back to single line if "it fits better"! That needs to be DISABLED, or a different tool be used!
- use airbnb style for ts etc.
- Unlimited line width, but prefer one-element-per line for arrays, html attributes, function params etc.
- make sure it formats Vue files, too.
- reminder that the config key is called `"markup": { …` not `"markup_fmt"`.

——————————

bash script get own file dir

——————————

```
🔍 Step 1: Check for lint errors
Running ruff check...
… ruff error output …
Found 1 error. [*] 1 fixable with the `--fix` option. make: *** [release] Error 1
```

Also insert a step where the linter has only fixable errors, so it commits the file before, then does an "autofix" commit afterwards - similar to the format ones.

The interesting part is, the first step already fails if it has those fixable issues - they are at that point still considered issues.

——————————

fatal: tag 'v0.0.0-pre19' already exists
Ask to move the tag (delete the old one and recreate as intended)

——————————
