# Why rewrite TNcontrol in go?

1. Codebase Scalability and Technical Debt: The Python code was becoming too large and unmanageable. My previous approach—shipping as much code as possible in the shortest amount of time—resulted in appalling code quality.

2. New Architectural Approach: I am changing how we handle Vesus timeout issues. Instead of querying Vesus, VegaResult, and CIGU18 every single time, the new version will perform a single, full data pull to build a local database. This approach also enables the possibility of viewing past tournaments.

3. Maintenance and Transition: While the Go version is under development, I will do my best to keep the Python version semi-stable and functional, though I can't make any firm guarantees. Once the Go version reaches feature parity with the Python version, it will be merged into the master branch, and the Python version will be deprecated.
