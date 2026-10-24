# Data sources and permissions

## CGMacros v1.0.0
- Creators: Ricardo Gutierrez-Osuna, David Kerr, Bobak Mortazavi, Anurag Das.
- Repository: https://physionet.org/content/cgmacros/1.0.0/
- DOI: https://doi.org/10.13026/3z8q-x658
- License: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International.
- License text: https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.en
- Original publication: Das et al., Scientific Data (2025), https://www.nature.com/articles/s41597-025-05851-7

The included `data/source_csv.zip` preserves the 45 participant CSVs and `bio.csv` obtained from the original PhysioNet archive. It excludes meal photographs and microbiome files, which the prototype does not use. Original CSV SHA-256 hashes are in `data/source_manifest.json`.

Modifications: normalized columns, converted timestamps, selected a conservative five-minute Dexcom phase and integer readings, aggregated wearable fields, divided METs by ten per the data dictionary, delayed dynamic inputs by fifteen minutes, and created five-minute processed tables. No new backward interpolation is added. One missing input bin can be forward-filled; targets are not filled. Meal amounts use the dataset's recorded gram quantities without an additional percentage correction. Baseline fields come from the same participant.

Processed tables, EHR-like JSON records and other data derivatives retain CC BY-NC-SA 4.0. Attribute the creators, identify modifications, retain this notice, and respect noncommercial/share-alike terms. This research package makes no claim of commercial data licensing. Obtain appropriate permissions before commercial use. No endorsement by the creators or Happiest Health is implied.

## Measurement limitations
The supplied one-minute glucose values were interpolated upstream. Native device exports are absent. Cadence/integer filtering and a fifteen-minute delay are conservative mitigations, not proof that every retained value is an original native observation. Some study participants have substantial missing coverage; see `data/audit.json`. Dates were shifted by the source. True logging latency for meals is unavailable. Activity is METs and heart rate, not invented step counts or sleep measurements.

## Clinical endpoint reference
Battelino et al. (2019), https://pubmed.ncbi.nlm.nih.gov/31177185/ supports commonly reported CGM ranges. The three-bin episode persistence rule is this project's engineering choice and is not a clinical prescription.

## Synthetic scenario sandbox
The scenario curve is original illustrative mathematics: an assumed carbohydrate impulse and assumed activity effect. It is not fitted to causal intervention data. No scenario effect is included in evaluation results or described as observed benefit.
