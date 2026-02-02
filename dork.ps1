param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

$root = $PSScriptRoot
python "$root\dork.py" @Args
