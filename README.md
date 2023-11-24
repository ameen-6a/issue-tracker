# Issue Tracker System

## Installation for macOS

```macOS
cd /django && 
pip install -r -requirements.tx
```

## Known Issues
- SQL injection
- No global exception handler
- No coverage test
- ORM have not been used properly for output
- Test case DB was connected to the real one because of raw connection

## To prevent race condition: 
- select_for_update() function is used for thread locking together with transaction.atomic() to make sure that no transactions are overlapped in the network layer during concurrency loads.