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

from barf.arch import ARCH_X86_MODE_32
from barf.arch import ARCH_X86_MODE_64
from barf.core.reil import ReilImmediateOperand
from barf.core.reil import ReilRegisterOperand


# "Control Transfer Instructions"
# ============================================================================ #
def _translate_address(self, tb, oprnd):
    addr_oprnd_size = oprnd.size + 8

    if isinstance(oprnd, ReilRegisterOperand):
        oprnd_tmp = tb.temporal(addr_oprnd_size)
        addr_oprnd = tb.temporal(addr_oprnd_size)
        imm = ReilImmediateOperand(8, addr_oprnd_size)

        tb.add(self._builder.gen_str(oprnd, oprnd_tmp))
        tb.add(self._builder.gen_bsh(oprnd_tmp, imm, addr_oprnd))
    elif isinstance(oprnd, ReilImmediateOperand):
        addr_oprnd = ReilImmediateOperand(oprnd.immediate << 8, addr_oprnd_size)

    return addr_oprnd


def _translate_jmp(self, tb, instruction):
    # Flags Affected
    # All flags are affected if a task switch occurs; no flags are
    # affected if a task switch does not occur.

    oprnd0 = tb.read(instruction.operands[0])

    addr_oprnd = _translate_address(self, tb, oprnd0)

    imm0 = tb.immediate(1, 1)

    tb.add(self._builder.gen_jcc(imm0, addr_oprnd))


def _translate_jcc(self, tb, instruction, jcc_cond):
    # Jump if condition (jcc_cond) is met.
    # Flags Affected
    # None.

    eval_cond_fn_name = "_evaluate_" + jcc_cond
    eval_cond_fn = getattr(self, eval_cond_fn_name, None)

    if not eval_cond_fn:
        raise NotImplementedError("Instruction Not Implemented")

    oprnd0 = tb.read(instruction.operands[0])

    addr_oprnd = _translate_address(self, tb, oprnd0)

    tb.add(self._builder.gen_jcc(eval_cond_fn(tb), addr_oprnd))


def _translate_ja(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'a')


def _translate_jae(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'ae')


def _translate_jb(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'b')


def _translate_jbe(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'be')


def _translate_jc(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'c')


def _translate_je(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'e')


def _translate_jg(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'g')


def _translate_jge(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'ge')


def _translate_jl(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'l')


def _translate_jle(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'le')


def _translate_jna(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'na')


def _translate_jnae(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'nae')


def _translate_jnb(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'nb')


def _translate_jnbe(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'nbe')


def _translate_jnc(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'nc')


def _translate_jne(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'ne')


def _translate_jng(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'ng')


def _translate_jnge(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'nge')


def _translate_jnl(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'nl')


def _translate_jnle(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'nle')


def _translate_jno(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'no')


def _translate_jnp(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'np')


def _translate_jns(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'ns')


def _translate_jnz(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'nz')


def _translate_jo(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'o')


def _translate_jp(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'p')


def _translate_jpe(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'pe')


def _translate_jpo(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'po')


def _translate_js(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 's')


def _translate_jz(self, tb, instruction):
    _translate_jcc(self, tb, instruction, 'z')


def _translate_jecxz(self, tb, instruction):
    # Jump short if ECX register is 0.

    oprnd0 = tb.read(instruction.operands[0])

    addr_oprnd = _translate_address(self, tb, oprnd0)

    tmp0 = tb.temporal(1)

    ecx = ReilRegisterOperand("ecx", 32)

    tb.add(self._builder.gen_bisz(ecx, tmp0))
    tb.add(self._builder.gen_jcc(tmp0, addr_oprnd))


def _translate_call(self, tb, instruction):
    # Flags Affected
    # All flags are affected if a task switch occurs; no flags are
    # affected if a task switch does not occur.

    oprnd0 = tb.read(instruction.operands[0])

    addr_oprnd = _translate_address(self, tb, oprnd0)

    imm1 = tb.immediate(1, 1)

    tmp0 = tb.temporal(self._sp.size)

    end_addr = ReilImmediateOperand((instruction.address + instruction.size), self._arch_info.address_size)

    tb.add(self._builder.gen_sub(self._sp, self._ws, tmp0))
    tb.add(self._builder.gen_str(tmp0, self._sp))
    tb.add(self._builder.gen_stm(end_addr, self._sp))
    tb.add(self._builder.gen_jcc(imm1, addr_oprnd))


def _translate_ret(self, tb, instruction):
    # Flags Affected
    # None.

    imm1 = tb.immediate(1, 1)
    imm8 = tb.immediate(8, self._sp.size)

    tmp0 = tb.temporal(self._sp.size)
    tmp1 = tb.temporal(self._sp.size)
    tmp2 = tb.temporal(self._sp.size + 8)

    tb.add(self._builder.gen_ldm(self._sp, tmp1))
    tb.add(self._builder.gen_add(self._sp, self._ws, tmp0))
    tb.add(self._builder.gen_str(tmp0, self._sp))

    # Free stack.
    if len(instruction.operands) > 0:
        oprnd0 = tb.read(instruction.operands[0])

        imm0 = tb.immediate(oprnd0.immediate & (2 ** self._sp.size - 1), self._sp.size)

        tmp3 = tb.temporal(self._sp.size)

        tb.add(self._builder.gen_add(self._sp, imm0, tmp3))
        tb.add(self._builder.gen_str(tmp3, self._sp))

    tb.add(self._builder.gen_bsh(tmp1, imm8, tmp2))
    tb.add(self._builder.gen_jcc(imm1, tmp2))


def _translate_loop(self, tb, instruction):
    # Flags Affected
    # None.

    if self._arch_mode == ARCH_X86_MODE_32:
        counter = ReilRegisterOperand("ecx", 32)
    elif self._arch_mode == ARCH_X86_MODE_64:
        counter = ReilRegisterOperand("rcx", 64)

    oprnd0 = tb.read(instruction.operands[0])

    addr_oprnd = _translate_address(self, tb, oprnd0)

    tmp0 = tb.temporal(counter.size)

    imm0 = tb.immediate(1, counter.size)

    tb.add(self._builder.gen_str(counter, tmp0))
    tb.add(self._builder.gen_sub(tmp0, imm0, counter))
    tb.add(self._builder.gen_jcc(counter, addr_oprnd))  # keep looping


def _translate_loopne(self, tb, instruction):
    # Flags Affected
    # None.

    if self._arch_mode == ARCH_X86_MODE_32:
        counter = ReilRegisterOperand("ecx", 32)
    elif self._arch_mode == ARCH_X86_MODE_64:
        counter = ReilRegisterOperand("rcx", 64)

    oprnd0 = tb.read(instruction.operands[0])

    addr_oprnd = _translate_address(self, tb, oprnd0)

    end_addr = ReilImmediateOperand((instruction.address + instruction.size) << 8, self._arch_info.address_size + 8)

    tmp0 = tb.temporal(counter.size)

    counter_zero = tb.temporal(1)
    counter_not_zero = tb.temporal(1)
    zf_zero = tb.temporal(1)
    branch_cond = tb.temporal(1)

    imm0 = tb.immediate(1, counter.size)
    imm1 = tb.immediate(1, 1)

    keep_looping_lbl = tb.label('keep_looping')

    tb.add(self._builder.gen_str(counter, tmp0))
    tb.add(self._builder.gen_sub(tmp0, imm0, counter))
    tb.add(self._builder.gen_bisz(counter, counter_zero))
    tb.add(self._builder.gen_bisz(self._flags["zf"], zf_zero))
    tb.add(self._builder.gen_xor(counter_zero, imm1, counter_not_zero))
    tb.add(self._builder.gen_and(counter_not_zero, zf_zero, branch_cond))
    tb.add(self._builder.gen_jcc(branch_cond, keep_looping_lbl))
    tb.add(self._builder.gen_jcc(imm0, end_addr))  # exit loop
    tb.add(keep_looping_lbl)
    tb.add(self._builder.gen_jcc(imm0, addr_oprnd))


def _translate_loopnz(self, tb, instruction):
    return _translate_loopne(self, tb, instruction)


def _translate_loope(self, tb, instruction):
    # Flags Affected
    # None.

    if self._arch_mode == ARCH_X86_MODE_32:
        counter = ReilRegisterOperand("ecx", 32)
    elif self._arch_mode == ARCH_X86_MODE_64:
        counter = ReilRegisterOperand("rcx", 64)

    oprnd0 = tb.read(instruction.operands[0])

    addr_oprnd = _translate_address(self, tb, oprnd0)

    end_addr = ReilImmediateOperand((instruction.address + instruction.size) << 8, self._arch_info.address_size + 8)

    tmp0 = tb.temporal(counter.size)

    counter_zero = tb.temporal(1)
    counter_not_zero = tb.temporal(1)
    zf_zero = tb.temporal(1)
    zf_not_zero = tb.temporal(1)
    branch_cond = tb.temporal(1)

    imm0 = tb.immediate(1, counter.size)
    imm1 = tb.immediate(1, 1)

    keep_looping_lbl = tb.label('keep_looping')

    tb.add(self._builder.gen_str(counter, tmp0))
    tb.add(self._builder.gen_sub(tmp0, imm0, counter))
    tb.add(self._builder.gen_bisz(counter, counter_zero))
    tb.add(self._builder.gen_bisz(self._flags["zf"], zf_zero))
    tb.add(self._builder.gen_xor(zf_zero, imm1, zf_not_zero))
    tb.add(self._builder.gen_xor(counter_zero, imm1, counter_not_zero))
    tb.add(self._builder.gen_and(counter_not_zero, zf_not_zero, branch_cond))
    tb.add(self._builder.gen_jcc(branch_cond, keep_looping_lbl))
    tb.add(self._builder.gen_jcc(imm0, end_addr))  # exit loop
    tb.add(keep_looping_lbl)
    tb.add(self._builder.gen_jcc(imm0, addr_oprnd))


def _translate_loopz(self, tb, instruction):
    return _translate_loope(self, tb, instruction)


dispatcher = {
    '_translate_jmp': _translate_jmp,
    '_translate_jcc': _translate_jcc,
    '_translate_ja': _translate_ja,
    '_translate_jae': _translate_jae,
    '_translate_jb': _translate_jb,
    '_translate_jbe': _translate_jbe,
    '_translate_jc': _translate_jc,
    '_translate_je': _translate_je,
    '_translate_jg': _translate_jg,
    '_translate_jge': _translate_jge,
    '_translate_jl': _translate_jl,
    '_translate_jle': _translate_jle,
    '_translate_jna': _translate_jna,
    '_translate_jnae': _translate_jnae,
    '_translate_jnb': _translate_jnb,
    '_translate_jnbe': _translate_jnbe,
    '_translate_jnc': _translate_jnc,
    '_translate_jne': _translate_jne,
    '_translate_jng': _translate_jng,
    '_translate_jnge': _translate_jnge,
    '_translate_jnl': _translate_jnl,
    '_translate_jnle': _translate_jnle,
    '_translate_jno': _translate_jno,
    '_translate_jnp': _translate_jnp,
    '_translate_jns': _translate_jns,
    '_translate_jnz': _translate_jnz,
    '_translate_jo': _translate_jo,
    '_translate_jp': _translate_jp,
    '_translate_jpe': _translate_jpe,
    '_translate_jpo': _translate_jpo,
    '_translate_js': _translate_js,
    '_translate_jz': _translate_jz,
    '_translate_jecxz': _translate_jecxz,
    '_translate_call': _translate_call,
    '_translate_ret': _translate_ret,
    '_translate_loop': _translate_loop,
    '_translate_loopne': _translate_loopne,
    '_translate_loopnz': _translate_loopnz,
    '_translate_loope': _translate_loope,
    '_translate_loopz': _translate_loopz,
}
