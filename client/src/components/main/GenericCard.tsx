import Image from "next/image";

interface NewsCardProps {
  img_url: string;
  original_img_width: number;
  original_img_height: number;
  is_large: boolean;
}

export default function GenericCard({
  img_url,
  original_img_width,
  original_img_height,
  is_large,
}: NewsCardProps) {
  return (
    <div
      className={`bg-card flex justify-center p-2 ${is_large ? "w-75 md:w-full" : "w-75"}`}
    >
      <div
        className={`flex flex-col justify-between ${is_large && "md:w-1/2"}`}
      >
        <div className="space-y-2">
          {/* Small image */}
          <Image
            src={img_url}
            alt="Placeholder image"
            className={`h-35 w-70 overflow-clip object-cover ${is_large && "md:hidden"}`}
            width={original_img_width}
            height={original_img_height}
          />
          <h6 className="text-card-foreground text-sm font-bold">
            Category / Date
          </h6>
          <h1 className="text-ink line-clamp-2 text-xl text-wrap">Title</h1>
          <h6 className="text-muted-foreground text-sm"> Date / Location </h6>
          <p className="text-ink line-clamp-3 text-sm text-wrap">
            Article / Description
          </p>
        </div>
        <button className="mt-2 w-full cursor-pointer border px-4 py-2">
          More Info / Read More
        </button>
      </div>
      {/* Large image */}
      {is_large && (
        <Image
          className="ml-2 hidden h-69 w-1/2 overflow-clip object-cover md:block"
          alt="Placeholder image"
          src={img_url}
          width={original_img_width}
          height={original_img_height}
        />
      )}
    </div>
  );
}
