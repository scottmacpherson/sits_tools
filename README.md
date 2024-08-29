A few little bits-and-bobs that might come in handy to other [SITS:Vision](https://www.tribalgroup.com/solutions/student-information-systems/sits-vision) developers.

## [PRB release order.sql]()

A little SQL script to quickly determine the build order (and therefor almost certainly the intended release order) for a list of projects.

### TODO

- [ ] Provide sample SRL syntax for rendering the output using DataTables.

## [SYDUPPBI01.sql]()

SQL script to find duplicate PBI records across all active and in-use projects. Menu options XPRJ2 and friends help find duplicate PRI records, but fails to account for what is actually built when project templates are used.

* The first `WITH` clause attaches a row number to all PRB records within their own PRJ when sorted by build date/time
* The second `WITH` clause uses that to get a list of all PBI records from the latest builds of all active and in-use projects
    * Excludes build items from `MENSYS.PRT` and `MENSYS.SLV` to reduce some noise
* The root `SELECT` uses that to return all build items with the same dictionary + entity + primary key that appear in more than one active project

### TODO

- [ ] Provide sample SRL syntax for rendering the output using DataTables.
