rule GenericVOneRule
{
	meta:
		description = "Generic Yara rule to detect Autofill data"
		author = "FH"
		date = "2025-01-27"
		version = "1.0"
		mwcp = "AutofillFinder.GenericVOne"
    strings:
        $special = /(login|name|email)\]?:\s*[^\n]+[$\n]/
        $family = "REDLINESUPPORT" ascii wide
        $password = /\*{44}\x0d\x0a\x0d\x0a(url|software|server)/i
    condition:
        $special and $family and not $password and uint8(0)!=0x7B
}
rule GenericTwo
{
    meta:
		description = "GenericRule to detect Autofill Stealer data"
		author = "FH"
		date = "2025-02-09"
		version = "1.0"
		mwcp = "AutofillFinder.GenericVTwo"
    strings:
        $form = /\x0a\x0aFORM:\s*[^\x0a]+\x0aV/
        $value = /\x0aVALUE:\s*[^\x0a]+\x0a\x0a/
    condition:
        $form and $value        
}
