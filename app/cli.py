import argparse, json, sys
from .models import ReviewRequest
from .pipeline import ReviewPipeline


def main() -> int:
    p = argparse.ArgumentParser(description="Review a local git checkout")
    p.add_argument("repo"); p.add_argument("--base", default="main"); p.add_argument("--head", default="HEAD"); p.add_argument("--pr", type=int, default=1)
    args = p.parse_args()
    try:
        result = ReviewPipeline().run(ReviewRequest(repo=args.repo, pr=args.pr, base=args.base, head=args.head))
        print(json.dumps({"summary": result.summary, "comments": [c.as_dict() for c in result.comments], "metadata": result.metadata}, indent=2))
        return 0
    except Exception as exc:
        print(f"review failed: {exc}", file=sys.stderr); return 1


if __name__ == "__main__": raise SystemExit(main())
