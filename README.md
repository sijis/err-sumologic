Err plugin for Sumologic
===

Requirements
---
```
pip install requests
```

Installation
---
```
!repos install https://github.com/sijis/err-sumologic.git
```

Usage
---
Simple example usage

```
!sumologic search _sourceCategory=prod Error
!sumologic search * | count by _sourceCategory
```
