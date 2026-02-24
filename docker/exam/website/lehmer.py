"""
Functions related to permuting lists with Lehmer codes
"""

from __future__ import annotations

import math
import random
import typing

class Permutation:
    """
    Represents a (immutable) permutation of a list.
    
    Has expected properties: `__eq__()`, `__hash__()`, `__repr__()`
    
    You can also apply the permutation to a sequence by calling
    `permutation(sequence)`. This will return a Python list, no matter
    what type of `Sequence` was orginally passed in.
    """
    
    def __init__(self, permutation: typing.Sequence[int],
            check: bool = True) -> None:
        """
        :param permutation: A list representing the permutation. Each integer
        from 0 to n must appear exactly once in the list (for an arbitrary
        integer n).
        :param check: Whether to check if the permutation is valid.
        :raises ValueError: If `check` is True and the sanity check
        fails.
        """
        if check:
            if 0 not in permutation:
                raise ValueError("Permutation must contain every number " + 
                        "between 0 and n.")
        self.__permutation: tuple[int, ...] = tuple(permutation)
    
    def __call__(self, sequence_to_permute: typing.Sequence) -> list:
        """
        Permutes a list. Takes in a sequence and returns a list
        :param sequence_to_permute: The `Sequence` for permutation
        """
        if self.n != len(sequence_to_permute):
            raise ValueError(f"Permutation of length {self.n} cannot be " + 
                    f"used to permute sequence with length {len(sequence_to_permute)}")
        permuted_sequence: list = list(sequence_to_permute)
        for map_src, map_dest in enumerate(self.permutation):
            permuted_sequence[map_dest] = sequence_to_permute[map_src]
        return permuted_sequence
    
    @property
    def permutation(self) -> tuple[int, ...]:
        """
        Gets the permutation information itself. Read-only
        """
        return self.__permutation
    
    @property
    def n(self) -> int:
        """
        The number of elements in the permutation. Read-only
        """
        return len(self.permutation)
    
    @staticmethod
    def from_lehmer(lehmer_code: int, n: int) -> Permutation:
        """
        Generate a `Permutation` object from a Lehmer code
        
        :param lehmer_code: The Lehmer code to generate the permutation
        from
        :param n: The number of elements in the Lehmer code.
        """
        lehmer_sequence: list[int] = []
        for i in range(n):
            lehmer_number: int = lehmer_code % (i+1)
            lehmer_sequence.insert(0, lehmer_number)
            lehmer_code //= (i+1)
        
        out_permutation: list[int] = []
        possible_values: list[int] = list(range(n))
        for i in lehmer_sequence:
            out_permutation.append(possible_values.pop(i))
        
        return Permutation(out_permutation, check=False)
    
    def to_lehmer(self) -> int:
        """
        Gets a Lehmer code for the permutation
        
        :return: An integer which can later be passed back into
        `from_lehmer` together with the appropriate `n` value to 
        yield this permutation.
        """
        lehmer_sequence: list[int] = []
        for i in range(self.n):
            lehmer_number: int = 0
            for j in range(i+1, self.n):
                if self.permutation[i] > self.permutation[j]:
                    lehmer_number += 1
            lehmer_sequence.append(lehmer_number)
        
        output_lehmer_value: int = 0
        for i, lehmer_number in enumerate(reversed(lehmer_sequence)):
            output_lehmer_value += (lehmer_number % (i+1)) * math.factorial(i)
        return output_lehmer_value
    
    def __eq__(self, other) -> bool:
        return self.permutation == other.permutation
    
    def __hash__(self) -> int:
        return hash(self.__permutation)
    
    def __repr__(self) -> str:
        return "Permutation(" + repr(self.__permutation) + ")"


def random_permutation(lbound: int, ubound: int) -> Permutation:
    """
    Gets a random permutation between a certain length.
    
    :param lbound: The lower bound for length (inclusive)
    :param ubound: The upper bound for permutation length (inclusive)
    :return: A random `Permutation` on arrays of the given length.
    """
    permutation_length: int = random.randint(lbound, ubound)
    generated_permutation: list[int] = list(range(permutation_length))
    random.shuffle(generated_permutation)
    return Permutation(generated_permutation)


if __name__ == "__main__":
    print("Starting unit tests for lehmer.py...")
    print("\n --- AUTOMATED TESTS ---")
    for _ in range(10):
        permutation_to_test: Permutation = random_permutation(5, 10)
        print("Testing permutation " + str(permutation_to_test) + "...")
        permutation_length: int = permutation_to_test.n
        permutation_lehmer: int = permutation_to_test.to_lehmer()
        assert permutation_to_test == Permutation.from_lehmer(permutation_lehmer, permutation_length), "Test failed"
        assert permutation_lehmer < math.factorial(permutation_length), \
                "Lehmer code exceeded maximum value"
    print("\n --- MANUAL TESTS ---")
    print("Please verify that the output is correct")
    print("Check that the permutation order of (3, 1, 0, 2) is correct")
    permutation_to_test = Permutation((3, 1, 0, 2))
    print(permutation_to_test("abcd"))