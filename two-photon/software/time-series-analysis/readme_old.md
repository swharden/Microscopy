## Rapid dG/R analysis with FIJI
sequence: GoR, bGoR, 

Option 1:
* load the .xml TSeries file by dragging/dropping onto FIJI
* for each stack, image > type > 32-bit
* delete the first slice of both layers: `run("Delete Slice");`
* rename layers to `R` and `G`

Option 2:
* in Explorer, select all Ch1 TIFs (except the first one) and drop in ImageJ
* Image > stack > images to stack, and set the name as `R`
* Do the same with all Ch2 TIFs (except the first one) and name it `G`

Resume with:
* Image > Image Expression Parser
 * set A:`R` and B:`G` (which is automatic)
 * Expression = `B/A` = `G/R`
 * rename the output `GoR`
* duplicate `GoR` and rename it `bGoR` (for baseline)
* Z-project only the baseline slices using averaging mode, and "copy" the result
* With `bGoR` selected, use the script below to paste into every slice
* Image > Image Expression Parser
 * set A:`R`, B:`bGoR`, and C:`GoR`
 * Expression = `(C-B)/A` = `((GoR)-(bGoR))/R`
 * rename the output `dGoR`

## Scripts #

**Paste into every slice of the selected stack:**
```java
for (var i=1; i<=nSlices; i++){
	setSlice(i);
	run("Paste");
}
```

