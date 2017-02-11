# invada
A dialogue engine development framework, based on response-pairs.

One response-pair consists of 3 components:
- matcher
- scorer
- generator

And, one-time response has 3 phases:
1. matching
2. scoring
3. generating

Matching is pattern-matchings by the matcher with the user utterance.
Scoring is computations the fitness of the response-pair with the user utterance.
Finally, generating is a generation of a bot utterance.

## Installation
```
pip install git+https://github.com/carrotflakes/invada.git
```

## License
This software is available under the MIT License.
