A few little bits-and-bobs that might come in handy to other [SITS:Vision](https://www.tribalgroup.com/solutions/student-information-systems/sits-vision) developers.

## [prb_release_order.sql](prb_release_order.sql)

A little (Oracle) SQL script to quickly determine the build order (and therefor almost certainly the intended release order) for a list of projects.

## [duplicate_pri_records.sql](duplicate_pri_records.sql)

(Oracle) SQL script to find duplicate PBI records across all active and in-use projects. Menu options XPRJ2 and friends help find duplicate PRI records, but fail to account for what is actually built when project templates are used.

* The first `WITH` clause attaches a row number to all PRB records within their own PRJ when sorted by build date/time
* The second `WITH` clause uses that to get a list of all PBI records from the latest builds of all active and in-use projects
    * Excludes build items from `MENSYS.PRT` and `MENSYS.SLV` to reduce some noise
* The root `SELECT` uses that to return all build items with the same dictionary + entity + primary key that appear in more than one active project

### [duplicate_pri_records.html](duplicate_pri_records.html)

Content of SRL which renders the output of `duplicate_pri_records.sql`.

1. Pop the SQL into an RQH/RQI
2. Set RQI "Output Mode" (`RQI_MODE`) to "List" (`MODE1`)
3. Create an SRL with the content of `duplicate_pri_records.html` and tweak as required, especially the call to `PSRS_YRQH.RUN` on line 19.
4. The usual POD/POP and COP stuff from there
