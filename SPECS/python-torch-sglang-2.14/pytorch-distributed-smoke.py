# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-License-Identifier: MIT
#
# Two-process native distributed smoke test for the built python-torch.  This
# deliberately fails when distributed or its Gloo backend is unavailable.
import datetime
import multiprocessing
import os
import shutil
import tempfile
import time
import traceback


_WORLD_SIZE = 2
_TIMEOUT_SECONDS = 90


def _worker(rank, rendezvous):
    import torch
    import torch.distributed as dist
    from torch.distributed import ReduceOp

    initialized = False
    try:
        if not dist.is_available():
            raise RuntimeError("torch.distributed is unavailable")
        if not dist.is_gloo_available():
            raise RuntimeError("torch.distributed Gloo backend is unavailable")

        dist.init_process_group(
            backend="gloo",
            init_method="file://" + rendezvous,
            rank=rank,
            world_size=_WORLD_SIZE,
            timeout=datetime.timedelta(seconds=_TIMEOUT_SECONDS),
        )
        initialized = True
        value = torch.tensor([rank + 1], dtype=torch.float32)
        dist.all_reduce(value, op=ReduceOp.SUM)
        if value.item() != 3.0:
            raise AssertionError(
                "Gloo all_reduce returned %s for rank %d" % (value.item(), rank)
            )
    except Exception:
        traceback.print_exc()
        raise
    finally:
        if initialized:
            dist.destroy_process_group()


def main():
    import torch.distributed as dist

    if not dist.is_available():
        raise RuntimeError("torch.distributed is unavailable")
    if not dist.is_gloo_available():
        raise RuntimeError("torch.distributed Gloo backend is unavailable")
    if not dist.is_backend_available("gloo"):
        raise RuntimeError("torch.distributed gloo backend is unavailable")
    from torch.distributed import Backend, ReduceOp

    if Backend.GLOO != "gloo" or ReduceOp.SUM is None:
        raise RuntimeError("torch.distributed Backend or ReduceOp is incomplete")

    rendezvous_dir = tempfile.mkdtemp(prefix="pytorch-distributed-smoke-")
    rendezvous = os.path.join(rendezvous_dir, "store")
    context = multiprocessing.get_context("spawn")
    processes = [
        context.Process(target=_worker, args=(rank, rendezvous), name="torch-rank-%d" % rank)
        for rank in range(_WORLD_SIZE)
    ]
    try:
        for process in processes:
            process.start()
        deadline = time.monotonic() + _TIMEOUT_SECONDS
        for process in processes:
            process.join(max(0, deadline - time.monotonic()))

        lingering = [process for process in processes if process.is_alive()]
        for process in lingering:
            process.terminate()
        for process in lingering:
            process.join(5)
        stuck = [process for process in lingering if process.is_alive()]
        for process in stuck:
            process.kill()
        for process in stuck:
            process.join(5)
        if lingering:
            raise RuntimeError(
                "distributed smoke timed out; terminated %s" % ", ".join(
                    process.name for process in lingering
                )
            )

        failed = [
            "%s (exit code %s)" % (process.name, process.exitcode)
            for process in processes
            if process.exitcode != 0
        ]
        if failed:
            raise RuntimeError("distributed smoke failed: " + ", ".join(failed))
    finally:
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join(5)
                if process.is_alive():
                    process.kill()
                    process.join(5)
        shutil.rmtree(rendezvous_dir)

    print("distributed smoke: PASS")


if __name__ == "__main__":
    main()
