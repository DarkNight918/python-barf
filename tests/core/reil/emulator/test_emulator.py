# Copyright (c) 2014, Fundacion Dr. Manuel Sadosky
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import absolute_import

import unittest

from barf.arch import ARCH_X86_MODE_32
from barf.arch.x86 import X86ArchitectureInformation
from barf.arch.x86.parser import X86Parser
from barf.arch.x86.translator import X86Translator
from barf.core.reil.container import ReilContainer
from barf.core.reil.container import ReilSequence
from barf.core.reil.emulator import ReilCpuInvalidAddressError
from barf.core.reil.emulator import ReilCpuZeroDivisionError
from barf.core.reil.emulator import ReilEmulator
from barf.core.reil.parser import ReilParser


class ReilEmulatorTests(unittest.TestCase):

    def setUp(self):
        self._arch_info = X86ArchitectureInformation(ARCH_X86_MODE_32)

        self._emulator = ReilEmulator(self._arch_info)

        self._asm_parser = X86Parser(ARCH_X86_MODE_32)
        self._reil_parser = ReilParser()

        self._translator = X86Translator(ARCH_X86_MODE_32)

    def test_add(self):
        asm_instrs  = self._asm_parser.parse("add eax, ebx")

        self.__set_address(0xdeadbeef, [asm_instrs])

        reil_instrs = self._translator.translate(asm_instrs)

        regs_initial = {
            "eax" : 0x1,
            "ebx" : 0x2,
        }

        regs_final, _ = self._emulator.execute_lite(
            reil_instrs,
            context=regs_initial
        )

        self.assertEqual(regs_final["eax"], 0x3)
        self.assertEqual(regs_final["ebx"], 0x2)

    def test_loop(self):
        # 0x08048060 : b8 00 00 00 00   mov eax,0x0
        # 0x08048065 : bb 0a 00 00 00   mov ebx,0xa
        # 0x0804806a : 83 c0 01         add eax,0x1
        # 0x0804806d : 83 eb 01         sub ebx,0x1
        # 0x08048070 : 83 fb 00         cmp ebx,0x0
        # 0x08048073 : 75 f5            jne 0x0804806a

        asm_instrs_str  = [(0x08048060, "mov eax,0x0", 5)]
        asm_instrs_str += [(0x08048065, "mov ebx,0xa", 5)]
        asm_instrs_str += [(0x0804806a, "add eax,0x1", 3)]
        asm_instrs_str += [(0x0804806d, "sub ebx,0x1", 3)]
        asm_instrs_str += [(0x08048070, "cmp ebx,0x0", 3)]
        asm_instrs_str += [(0x08048073, "jne 0x0804806a", 2)]

        asm_instrs = []

        for addr, asm, size in asm_instrs_str:
            asm_instr = self._asm_parser.parse(asm)
            asm_instr.address = addr
            asm_instr.size = size

            asm_instrs.append(asm_instr)

        reil_instrs = self.__translate(asm_instrs)

        regs_final, _ = self._emulator.execute(
            reil_instrs,
            start=0x08048060 << 8
        )

        self.assertEqual(regs_final["eax"], 0xa)
        self.assertEqual(regs_final["ebx"], 0x0)

    def test_mov(self):
        asm_instrs  = [self._asm_parser.parse("mov eax, 0xdeadbeef")]
        asm_instrs += [self._asm_parser.parse("mov al, 0x12")]
        asm_instrs += [self._asm_parser.parse("mov ah, 0x34")]

        self.__set_address(0xdeadbeef, asm_instrs)

        reil_instrs  = self._translator.translate(asm_instrs[0])
        reil_instrs += self._translator.translate(asm_instrs[1])
        reil_instrs += self._translator.translate(asm_instrs[2])

        regs_initial = {
            "eax" : 0xffffffff,
        }

        regs_final, _ = self._emulator.execute_lite(reil_instrs, context=regs_initial)

        self.assertEqual(regs_final["eax"], 0xdead3412)

    def test_pre_handler(self):
        def pre_handler(emulator, instruction, parameter):
            paramter.append(True)

        asm = ["mov eax, ebx"]

        x86_instrs = [self._asm_parser.parse(i) for i in asm]
        self.__set_address(0xdeadbeef, x86_instrs)
        reil_instrs = [self._translator.translate(i) for i in x86_instrs]

        paramter = []

        self._emulator.set_instruction_pre_handler(pre_handler, paramter)

        reil_ctx_out, reil_mem_out = self._emulator.execute_lite(
            reil_instrs[0]
        )

        self.assertTrue(len(paramter) > 0)

    def test_post_handler(self):
        def post_handler(emulator, instruction, parameter):
            paramter.append(True)

        asm = ["mov eax, ebx"]

        x86_instrs = [self._asm_parser.parse(i) for i in asm]
        self.__set_address(0xdeadbeef, x86_instrs)
        reil_instrs = [self._translator.translate(i) for i in x86_instrs]

        paramter = []

        self._emulator.set_instruction_post_handler(post_handler, paramter)

        _, _ = self._emulator.execute_lite(
            reil_instrs[0]
        )

        self.assertTrue(len(paramter) > 0)

    def test_zero_division_error_1(self):
        asm_instrs  = [self._asm_parser.parse("div ebx")]

        self.__set_address(0xdeadbeef, asm_instrs)

        reil_instrs  = self._translator.translate(asm_instrs[0])

        regs_initial = {
            "eax" : 0x2,
            "edx" : 0x2,
            "ebx" : 0x0,
        }

        self.assertRaises(ReilCpuZeroDivisionError, self._emulator.execute_lite, reil_instrs, context=regs_initial)

    def test_zero_division_error_2(self):
        instrs = ["mod [DWORD eax, DWORD ebx, DWORD t0]"]

        reil_instrs = self._reil_parser.parse(instrs)

        reil_instrs[0].address = 0xdeadbeef00

        regs_initial = {
            "eax" : 0x2,
            "ebx" : 0x0,
        }

        self.assertRaises(ReilCpuZeroDivisionError, self._emulator.execute_lite, reil_instrs, context=regs_initial)

    def test_invalid_address_error_1(self):
        asm_instrs = [self._asm_parser.parse("jmp eax")]

        self.__set_address(0xdeadbeef, asm_instrs)

        reil_instrs = self.__translate(asm_instrs)

        regs_initial = {
            "eax" : 0xffffffff,
        }

        self.assertRaises(ReilCpuInvalidAddressError, self._emulator.execute, reil_instrs, start=0xdeadbeef << 8, registers=regs_initial)

    def test_invalid_address_error_2(self):
        asm_instrs = [self._asm_parser.parse("mov eax, 0xdeadbeef")]

        self.__set_address(0xdeadbeef, asm_instrs)

        reil_instrs = self.__translate(asm_instrs)

        regs_initial = {
            "eax" : 0xffffffff,
        }

        self.assertRaises(ReilCpuInvalidAddressError, self._emulator.execute, reil_instrs, start=0xdeadbef0 << 8, registers=regs_initial)

    # Auxiliary methods
    # ======================================================================== #
    def __set_address(self, address, asm_instrs):
        addr = address

        for asm_instr in asm_instrs:
            asm_instr.address = addr
            addr += 1

    def __translate(self, asm_instrs):
        instr_container = ReilContainer()

        asm_instr_last = None
        instr_seq_prev = None

        for asm_instr in asm_instrs:
            instr_seq = ReilSequence()

            for reil_instr in self._translator.translate(asm_instr):
                instr_seq.append(reil_instr)

            if instr_seq_prev:
                instr_seq_prev.next_sequence_address = instr_seq.address

            instr_container.add(instr_seq)

            instr_seq_prev = instr_seq

        if instr_seq_prev:
            if asm_instr_last:
                instr_seq_prev.next_sequence_address = (asm_instr_last.address + asm_instr_last.size) << 8

        # instr_container.dump()

        return instr_container


def main():
    unittest.main()


if __name__ == '__main__':
    main()
