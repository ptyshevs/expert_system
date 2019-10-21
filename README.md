## Expert System - Propositional Inference Calculator

### Bonuses

* Interactive mode
* Verbose mode
* Xor in conclusion
* Or in conclusion
* IFF (equivalence)

### Truth Tables

Implication

| X | Y | X => Y |
|---|---|---------|
|0 | 0 | 1|
|0 | 1 | 1|
|1 | 0 | 0|
|1 | 1 | 1|

Equivalence

| X | Y | X <=> Y |
|---|---|---------|
|0 | 0 | 1|
|0 | 1 | 0|
|1 | 0 | 0|
|1 | 1 | 1|

### Design doc

Expert system consists of:

Set of rules in format Condition => Conclusion, where both Condition and Conclusion can be Expression.

If we solve condition, we can say what conclusion term should evaluate for:

```
A => B

=

?B
```

Ths can be written as statement: "if 10 > 42 then Pavel eats chocolate cupcakes".
Since condition is False, we don't have sufficient information to tell anything about the conclusion. However, if it's True, the result totally depends on right side.

### Acknowledgement

[Pseudo-code](./doc) is a courtesy of [@elyahove](https://github.com/ely-uf)
